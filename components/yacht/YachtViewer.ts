import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";
import { SERVICES, OVERVIEW, INSIDE, PART_LABELS, type ServiceId, type CameraPreset } from "@/lib/services";

export type ViewerStatus =
  | { state: "loading"; progress: number | null }
  | { state: "ready" }
  | { state: "error"; message: string };

export interface ViewerState {
  id: ServiceId | null;
  xray: boolean;
}

export interface ViewerOptions {
  canvas: HTMLCanvasElement;
  tip: HTMLElement;
  modelUrl: string;
  /** Overlays the camera should keep the yacht clear of. */
  getLayout: () => { card: HTMLElement | null; head: HTMLElement | null; desktop: boolean };
  /** Called when the visitor taps a part of the yacht. */
  onPick: (id: ServiceId) => void;
  onStatus: (status: ViewerStatus) => void;
  /** Current selection when the model finishes loading. */
  getState: () => ViewerState;
}

interface PartData {
  orig: THREE.Material | THREE.Material[];
  svc: ServiceId | null;
  label: string | null;
  internal: boolean; // hidden unless the inside view is on
  detailed: boolean; // added systems: keep true colours when highlighted
  shell: boolean; // becomes see-through in the inside view
  edges?: THREE.LineSegments;
}

// Parts of the hull, deck and superstructure that turn see-through in the inside view.
const SHELL =
  /^(hull_(topside|bottom|glazing)|spray_rail|sheer_shadow|accent_|bow_mark|main_deck|house_|windshield|transom$|transom_accent|coaming|garage_|sunpad$|deck_hatch|foredeck_hatch|anchor_locker|cockpit_bench|bench_back)/;
// Large shell parts that get a thin blue outline in the inside view.
const OUTLINE = /^(hull_topside|hull_bottom|main_deck|house_roof|house_side_lower|windshield|transom$)/;

/** The loader renames repeated nodes ("propeller", "propeller_1"); compare on the base name. */
const baseName = (n: string) => n.replace(/_\d+$/, "");

const partToService: Record<string, ServiceId> = {};
(Object.keys(SERVICES) as ServiceId[]).forEach((id) =>
  SERVICES[id].parts.forEach((p) => {
    if (!partToService[p]) partToService[p] = id;
  }),
);

function serviceOf(obj: THREE.Object3D): ServiceId | null {
  for (let o: THREE.Object3D | null = obj; o; o = o.parent) {
    const n = baseName(o.name);
    if (partToService[n]) return partToService[n];
    for (const id of Object.keys(SERVICES) as ServiceId[]) {
      if (SERVICES[id].prefixes.some((p) => n.startsWith(p))) return id;
    }
  }
  return null;
}

function labelOf(obj: THREE.Object3D): string | null {
  for (let o: THREE.Object3D | null = obj; o; o = o.parent) {
    const n = baseName(o.name);
    let best: string | null = null;
    for (const k in PART_LABELS) if (n.startsWith(k) && (!best || k.length > best.length)) best = k;
    if (best) return PART_LABELS[best];
  }
  return null;
}

function hasAncestor(obj: THREE.Object3D, test: (name: string) => boolean): boolean {
  for (let o: THREE.Object3D | null = obj; o; o = o.parent) {
    if (test(o.name) || test(baseName(o.name))) return true;
  }
  return false;
}

const ease = (x: number) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);

export class YachtViewer {
  private opts: ViewerOptions;
  private renderer: THREE.WebGLRenderer;
  private scene = new THREE.Scene();
  private camera = new THREE.PerspectiveCamera(30, 1, 1.0, 160);
  private controls: OrbitControls;
  private reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  private meshes: THREE.Mesh[] = [];
  private parts = new Map<THREE.Mesh, PartData>();
  private pickable: THREE.Mesh[] = [];
  private state: ViewerState = { id: null, xray: false };
  private loaded = false;

  private effAspect = 1.6;
  private tween: { from: THREE.Vector3; fromT: THREE.Vector3; to: THREE.Vector3; toT: THREE.Vector3; start: number; dur: number } | null = null;
  private visible = true;
  private raf = 0;
  private disposed = false;

  private ray = new THREE.Raycaster();
  private ptr = new THREE.Vector2();
  private down: { x: number; y: number } | null = null;

  private resizeObs: ResizeObserver;
  private visObs: IntersectionObserver;

  private mats = {
    clay: new THREE.MeshStandardMaterial({ color: 0xf3f6f8, roughness: 0.85, metalness: 0, side: THREE.DoubleSide }),
    clayInside: new THREE.MeshStandardMaterial({ color: 0xdce3e9, roughness: 0.8, metalness: 0 }),
    glow: new THREE.MeshStandardMaterial({
      color: 0x195c8f, roughness: 0.5, metalness: 0, emissive: 0x195c8f, emissiveIntensity: 0.12, envMapIntensity: 0.3, side: THREE.DoubleSide,
    }),
    ghost: new THREE.MeshStandardMaterial({
      color: 0xe4ecf3, roughness: 1, metalness: 0, transparent: true, opacity: 0.1, depthWrite: false, side: THREE.DoubleSide,
    }),
    edge: new THREE.LineBasicMaterial({ color: 0x195c8f, transparent: true, opacity: 0.28, depthWrite: false }),
  };

  constructor(opts: ViewerOptions) {
    this.opts = opts;
    const { canvas } = opts;

    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 0.92;
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    const pmrem = new THREE.PMREMGenerator(this.renderer);
    this.scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
    pmrem.dispose();

    this.controls = new OrbitControls(this.camera, canvas);
    Object.assign(this.controls, {
      enableDamping: true, dampingFactor: 0.08, enablePan: false, enableZoom: false,
      rotateSpeed: 0.7, maxPolarAngle: Math.PI * 0.6, autoRotate: !this.reduceMotion, autoRotateSpeed: 0.35,
    });

    // Physically based light units: intensities are scaled by pi relative to three.js' old "legacy" lights.
    const sun = new THREE.DirectionalLight(0xffffff, 1.1 * Math.PI);
    sun.position.set(8, 26, 14);
    sun.castShadow = true;
    sun.shadow.mapSize.set(2048, 2048);
    Object.assign(sun.shadow.camera, { left: -20, right: 20, top: 12, bottom: -12, near: 1, far: 60 });
    sun.shadow.bias = -0.0004;
    sun.shadow.normalBias = 0.03;
    this.scene.add(sun, new THREE.HemisphereLight(0xffffff, 0xdfe6ec, 0.45 * Math.PI));

    const ground = new THREE.Mesh(new THREE.PlaneGeometry(90, 90), new THREE.ShadowMaterial({ opacity: 0.1 }));
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -0.34;
    ground.receiveShadow = true;
    this.scene.add(ground);

    this.resizeObs = new ResizeObserver(() => this.resize());
    this.resizeObs.observe(canvas);
    this.visObs = new IntersectionObserver(([e]) => (this.visible = e.isIntersecting), { rootMargin: "100px" });
    this.visObs.observe(canvas);
    this.resize();

    canvas.addEventListener("pointerdown", this.onPointerDown);
    canvas.addEventListener("pointerup", this.onPointerUp);
    canvas.addEventListener("pointermove", this.onPointerMove);
    canvas.addEventListener("pointerleave", this.onPointerLeave);

    this.load();
    this.raf = requestAnimationFrame(this.loop);
  }

  /** Select a service (or none) and switch the inside view on or off. */
  show(id: ServiceId | null, xray: boolean) {
    this.controls.autoRotate = false;
    this.state = { id, xray };
    this.applyMaterials();
    this.flyTo(id ? SERVICES[id].cam : xray ? INSIDE : OVERVIEW);
  }

  dispose() {
    this.disposed = true;
    cancelAnimationFrame(this.raf);
    this.resizeObs.disconnect();
    this.visObs.disconnect();
    const c = this.opts.canvas;
    c.removeEventListener("pointerdown", this.onPointerDown);
    c.removeEventListener("pointerup", this.onPointerUp);
    c.removeEventListener("pointermove", this.onPointerMove);
    c.removeEventListener("pointerleave", this.onPointerLeave);
    this.controls.dispose();
    this.scene.traverse((o) => {
      const m = o as THREE.Mesh;
      m.geometry?.dispose();
      const mat = m.material;
      if (Array.isArray(mat)) mat.forEach((x) => x.dispose());
      else mat?.dispose();
    });
    Object.values(this.mats).forEach((m) => m.dispose());
    this.renderer.dispose();
  }

  // ------------------------------------------------------------------ loading

  private load() {
    this.opts.onStatus({ state: "loading", progress: 0 });
    new GLTFLoader().load(
      this.opts.modelUrl,
      (gltf) => {
        if (this.disposed) return;
        gltf.scene.traverse((o) => {
          const mesh = o as THREE.Mesh;
          if (!mesh.isMesh) return;
          const mat = mesh.material as THREE.MeshStandardMaterial;
          // Painted stripes sit on the hull surface; nudge them forward to avoid z-fighting.
          if (/dpv_blue|dpv_red|graphite/.test(mat.name)) {
            mat.polygonOffset = true;
            mat.polygonOffsetFactor = -2;
            mat.polygonOffsetUnits = -4;
          }
          mesh.castShadow = true;
          mesh.receiveShadow = true;
          const data: PartData = {
            orig: mesh.material,
            svc: serviceOf(mesh),
            label: labelOf(mesh),
            internal: hasAncestor(mesh, (n) => n === "systems_internal"),
            detailed: hasAncestor(mesh, (n) => n === "systems_internal" || n === "details_external"),
            shell: hasAncestor(mesh, (n) => SHELL.test(n)),
          };
          if (hasAncestor(mesh, (n) => OUTLINE.test(n))) {
            data.edges = new THREE.LineSegments(new THREE.EdgesGeometry(mesh.geometry, 28), this.mats.edge);
            data.edges.visible = false;
            mesh.add(data.edges);
          }
          this.parts.set(mesh, data);
          this.meshes.push(mesh);
        });
        this.scene.add(gltf.scene);
        const p = this.frame(OVERVIEW);
        this.camera.position.copy(p.pos);
        this.controls.target.copy(p.target);
        this.controls.update();
        this.loaded = true;

        this.state = this.opts.getState();
        this.applyMaterials();
        if (this.state.id || this.state.xray) this.flyTo(this.state.id ? SERVICES[this.state.id].cam : INSIDE);
        this.opts.onStatus({ state: "ready" });
      },
      (e) => {
        if (e.lengthComputable && e.total) this.opts.onStatus({ state: "loading", progress: e.loaded / e.total });
      },
      () => this.opts.onStatus({ state: "error", message: "The 3D model couldn't be loaded. The services are listed alongside." }),
    );
  }

  // ------------------------------------------------------------------ materials

  private applyMaterials() {
    if (!this.loaded) return;
    const { id, xray } = this.state;
    const { clay, clayInside, glow, ghost } = this.mats;
    for (const mesh of this.meshes) {
      const d = this.parts.get(mesh)!;
      if (d.edges) d.edges.visible = xray;
      if (d.internal) mesh.visible = xray;
      mesh.castShadow = !(xray && d.shell);
      if (xray && d.shell && !(id && d.svc === id)) {
        mesh.material = ghost;
        continue;
      }
      if (!id) {
        mesh.material = d.orig;
        continue;
      }
      mesh.material = d.svc === id ? (d.detailed ? d.orig : glow) : d.internal ? clayInside : clay;
    }
    this.pickable = this.meshes.filter((m) => m.visible && this.parts.get(m)!.svc && m.material !== ghost);
  }

  // ------------------------------------------------------------------ camera

  /** Keep the yacht centred in the open area, clear of the floating card and heading. */
  private resize() {
    const { canvas } = this.opts;
    const w = canvas.clientWidth;
    const h = canvas.clientHeight;
    if (!w || !h) return;
    this.renderer.setSize(w, h, false);
    this.camera.aspect = w / h;
    const { card, head, desktop } = this.opts.getLayout();
    let ox = 0, oy = 0, ew = w, eh = h;
    if (desktop && card) {
      const cw = card.offsetWidth + 40;
      ox = cw / 2;
      ew = w - cw;
    }
    if (head) {
      const hh = head.offsetTop + head.offsetHeight;
      const d = desktop ? hh * 0.22 : hh * 0.45;
      oy = -d;
      eh = h - d * 2;
    }
    this.camera.setViewOffset(w, h, ox, oy, w, h);
    this.camera.updateProjectionMatrix();
    this.effAspect = ew / Math.max(eh, 1);
  }

  private frame(p: CameraPreset) {
    const target = new THREE.Vector3(...p.target);
    const pos = new THREE.Vector3(...p.pos);
    const k = Math.min(2.7, Math.max(1.3, 2.25 / this.effAspect)); // pull back on narrow screens
    pos.sub(target).multiplyScalar(k).add(target);
    return { pos, target };
  }

  private flyTo(p: CameraPreset) {
    const { pos, target } = this.frame(p);
    if (this.reduceMotion || !this.loaded) {
      this.camera.position.copy(pos);
      this.controls.target.copy(target);
      this.controls.update();
      return;
    }
    this.tween = {
      from: this.camera.position.clone(), fromT: this.controls.target.clone(),
      to: pos, toT: target, start: performance.now(), dur: 1100,
    };
  }

  private loop = (now: number) => {
    this.raf = requestAnimationFrame(this.loop);
    if (!this.visible) return;
    if (this.tween) {
      const t = this.tween;
      const k = Math.min(1, (now - t.start) / t.dur);
      const e = ease(k);
      this.camera.position.lerpVectors(t.from, t.to, e);
      this.controls.target.lerpVectors(t.fromT, t.toT, e);
      if (k >= 1) this.tween = null;
    }
    this.controls.update();
    this.renderer.render(this.scene, this.camera);
  };

  // ------------------------------------------------------------------ picking

  private pick(ev: PointerEvent) {
    const r = this.opts.canvas.getBoundingClientRect();
    this.ptr.set(((ev.clientX - r.left) / r.width) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1);
    this.ray.setFromCamera(this.ptr, this.camera);
    const hit = this.ray.intersectObjects(this.pickable, false)[0];
    if (!hit) return null;
    const d = this.parts.get(hit.object as THREE.Mesh)!;
    return { svc: d.svc as ServiceId, label: d.label, x: ev.clientX - r.left, y: ev.clientY - r.top };
  }

  private onPointerDown = (e: PointerEvent) => {
    this.down = { x: e.clientX, y: e.clientY };
    this.controls.autoRotate = false;
  };

  private onPointerUp = (e: PointerEvent) => {
    if (this.down && Math.hypot(e.clientX - this.down.x, e.clientY - this.down.y) < 6) {
      const h = this.pick(e);
      if (h) this.opts.onPick(h.svc);
    }
    this.down = null;
  };

  private onPointerMove = (e: PointerEvent) => {
    const { tip, canvas } = this.opts;
    if (e.pointerType !== "mouse" || e.buttons) {
      tip.classList.remove("show");
      return;
    }
    const h = this.pick(e);
    canvas.style.cursor = h ? "pointer" : "";
    if (!h) {
      tip.classList.remove("show");
      return;
    }
    const title = document.createElement("strong");
    title.textContent = h.label ?? SERVICES[h.svc].name;
    const sub = document.createElement("span");
    sub.textContent = SERVICES[h.svc].name;
    tip.replaceChildren(title, ...(h.label ? [sub] : []));
    tip.style.left = `${h.x}px`;
    tip.style.top = `${h.y}px`;
    tip.classList.add("show");
  };

  private onPointerLeave = () => {
    this.opts.tip.classList.remove("show");
    this.opts.canvas.style.cursor = "";
  };
}
