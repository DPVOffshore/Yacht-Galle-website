/**
 * The six service disciplines, and how each maps onto the 3D yacht.
 *
 * - `parts`    exact node names from the original model (public/models/*.glb)
 * - `prefixes` name prefixes of the detailed parts added by scripts/model/build_detailed_model.py
 * - `xray`     whether selecting the service opens the see-through "inside" view
 * - `cam`      camera position and look-at target, in the model's own coordinates
 *              (bow = +x, starboard = +z, up = +y, metres)
 */

export type ServiceId = "hull" | "osmosis" | "engine" | "electrical" | "nav" | "interior";

export interface CameraPreset {
  pos: [number, number, number];
  target: [number, number, number];
}

export interface Service {
  name: string;
  desc: string;
  items: string[];
  parts: string[];
  prefixes: string[];
  xray: boolean;
  cam: CameraPreset;
}

export const SERVICE_ORDER: ServiceId[] = ["hull", "osmosis", "engine", "electrical", "nav", "interior"];

export const SERVICES: Record<ServiceId, Service> = {
  hull: {
    name: "Hull, paint and fibreglass",
    desc: "Hull maintenance and repair, expert painting and refinishing, and skilled fibreglass and wood repairs that restore structural integrity and finish.",
    items: [
      "Hull inspection and repair",
      "Painting and refinishing",
      "Fibreglass, gelcoat and structural repair",
      "Deck hardware, ladders and fittings",
    ],
    parts: [
      "hull_topside_stbd", "hull_topside_port", "spray_rail_stbd", "spray_rail_port", "transom",
      "accent_blue_stbd", "accent_blue_port", "accent_red_stbd", "accent_red_port",
      "bow_mark_blue_1_port", "bow_mark_blue_1_stbd", "bow_mark_blue_2_port", "bow_mark_blue_2_stbd",
      "bow_mark_red_port", "bow_mark_red_stbd", "main_deck", "house_side_lower_port", "house_side_lower_stbd",
      "house_roof", "coaming_port", "coaming_stbd", "coaming_cap_port", "coaming_cap_stbd",
      "garage_door", "swim_platform", "platform_strut", "transom_step",
    ],
    prefixes: ["hull_str_", "hw_"],
    xray: false,
    cam: { pos: [14, 6, 25], target: [0, 1.3, 0] },
  },
  osmosis: {
    name: "Anti-osmosis treatment",
    desc: "Protection for the hull below the waterline, preventing blistering and water ingress for long-term durability, using industry-leading techniques and materials.",
    items: ["Hull moisture assessment", "Blister repair", "Protective barrier coatings", "Long-term hull durability"],
    parts: ["hull_bottom_stbd", "hull_bottom_port"],
    prefixes: [],
    xray: false,
    cam: { pos: [19, -3.4, 21], target: [0.5, 0.3, 0] },
  },
  engine: {
    name: "Engines and propellers",
    desc: "A full range of engine services, from routine maintenance to complete overhauls and re-engine projects, through the drives, shafts and propellers to the fuel and exhaust systems.",
    items: [
      "Engine servicing and complete overhauls",
      "Re-engine projects",
      "Drives, shafts and propellers",
      "Fuel, cooling and exhaust systems",
    ],
    parts: [
      "propeller", "drive_nacelle", "drive_strut", "drive_boot", "steering_ram", "trim_interceptor",
      "exhaust_port", "vent_louver", "vent_recess", "bow_thruster_tunnel",
    ],
    prefixes: ["eng_"],
    xray: true,
    cam: { pos: [-18.5, 7, 9.5], target: [-10.2, 0.1, 0] },
  },
  electrical: {
    name: "Electrical and lighting",
    desc: "Electrical system services for safety and reliability, from generators, batteries and switchboards to upgrades, repairs, new installations and energy-efficient LED lighting.",
    items: [
      "Generators and battery banks",
      "Switchboards, inverters and shore power",
      "Fault finding, upgrades and new installations",
      "LED, underwater and navigation lighting",
    ],
    parts: [
      "house_accent_port", "house_accent_stbd", "coaming_accent_port", "coaming_accent_stbd",
      "garage_accent_blue", "transom_accent_blue", "arch_accent_blue",
    ],
    prefixes: ["elec_"],
    xray: true,
    cam: { pos: [-16, 9, 13], target: [-7, 0.5, 0] },
  },
  nav: {
    name: "Navigation and communication",
    desc: "Installation, calibration and repair of navigation and communication systems, so the helm reads true and you stay connected and informed on the water.",
    items: ["Radar, satcom and antennas", "Helm displays and autopilot", "Installation and calibration", "Repair and fault finding"],
    parts: ["radar_arch", "radar_dome", "antenna_whip", "helm_console", "helm_dash", "helm_wheel", "helm_wheel_hub"],
    prefixes: ["nav_"],
    xray: true,
    cam: { pos: [-8, 9, 12], target: [0.8, 2.3, 0] },
  },
  interior: {
    name: "Upholstery and carpentry",
    desc: "Custom upholstery for comfortable, stylish interiors and expert carpentry for cabins, saloon and deck, from repairs to full renovations and custom joinery.",
    items: [
      "Custom upholstery and soft furnishings",
      "Cabin and saloon joinery",
      "Galley and furniture renovation",
      "Teak and custom deck projects",
    ],
    parts: [
      "sunpad", "bow_sunpad", "cockpit_bench", "bench_back", "helm_seat", "helm_seat_back",
      "saloon_settee", "deck_hatch_fwd", "deck_hatch_aft", "foredeck_hatch",
    ],
    prefixes: ["int_"],
    xray: true,
    cam: { pos: [7, 13, 12], target: [1.2, 0, 0] },
  },
};

/** Default view of the whole yacht, and the default view when "See inside" is on. */
export const OVERVIEW: CameraPreset = { pos: [21, 8.5, 25], target: [-0.5, 1.1, 0] };
export const INSIDE: CameraPreset = { pos: [-3, 14, 16], target: [-2.5, 0.2, 0] };

/** Intro copy shown in the panel when no service is selected. */
export const PANEL_INTRO = {
  title: "Six disciplines, one team",
  desc: "From below the waterline to the top of the radar arch, we cover the whole yacht, inside and out. You deal with one team and receive one quote.",
};

/** Friendly names shown when hovering a part. Keys are node-name prefixes; the longest match wins. */
export const PART_LABELS: Record<string, string> = {
  eng_block: "Main engine, V12 diesel",
  eng_valvecover: "Cylinder heads and valve covers",
  eng_intercooler: "Charge-air cooler",
  eng_airfilter: "Air filter",
  eng_frontend: "Pulleys, belt and alternator",
  eng_heatex: "Heat exchanger and expansion tank",
  eng_oilfilter: "Oil filters",
  eng_ecu: "Engine control unit",
  eng_flywheel: "Flywheel housing",
  eng_muffler: "Water-lift muffler",
  eng_gearbox: "Gearbox",
  eng_shaft: "Drive shaft",
  eng_turbo: "Turbocharger",
  eng_exhaust: "Exhaust manifold and piping",
  eng_tank: "Fuel tank",
  eng_fuelline: "Fuel line",
  eng_mount: "Engine mount",
  eng_seacock: "Sea strainer and seacock",
  elec_genset: "Generator",
  elec_battery: "Battery bank",
  elec_switchboard: "Main switchboard",
  elec_inverter: "Inverter charger",
  elec_cable: "Cable run",
  elec_tray: "Cable tray",
  elec_shorepower: "Shore power inlet",
  elec_led_underwater: "Underwater lights",
  elec_navlight: "Navigation lights",
  elec_searchlight: "Searchlight",
  elec_led_strip: "LED courtesy lighting",
  nav_mfd: "Helm displays",
  nav_throttle: "Engine controls",
  nav_joystick: "Docking joystick",
  nav_compass: "Compass",
  nav_satcom: "Satcom dome",
  nav_gps: "GPS antenna",
  nav_antenna: "VHF antenna",
  nav_radar: "Open-array radar",
  nav_blackbox: "Navigation electronics",
  int_sole: "Cabin sole",
  int_bulkhead: "Bulkhead joinery",
  int_door: "Cabin door",
  int_bed: "Cabin berth",
  int_headboard: "Upholstered headboard",
  int_pillow: "Cushions",
  int_nightstand: "Nightstand",
  int_lamp: "Reading lamp",
  int_wardrobe: "Wardrobe",
  int_sofa: "Cabin seating",
  int_stairs: "Companionway stairs",
  int_table: "Table",
  int_galley: "Galley",
  hull_str_bearer: "Engine bearers",
  hw_ladder: "Swim ladder",
  hw_anchor: "Anchor",
  hw_chain: "Anchor chain",
  propeller: "Propeller",
  drive_nacelle: "Pod drive",
  radar_dome: "Radar",
  hull_bottom: "Hull below the waterline",
};
