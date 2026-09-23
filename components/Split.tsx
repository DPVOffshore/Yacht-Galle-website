import { Fragment } from "react";

/** Wraps each word in masked spans so headings can rise in word by word. `from` continues the stagger index. */
export function Split({ text, from = 0 }: { text: string; from?: number }) {
  const words = text.split(" ");
  return (
    <>
      {words.map((w, i) => (
        <Fragment key={i}>
          <span className="w" style={{ "--i": from + i } as React.CSSProperties}>
            <span>{w}</span>
          </span>
          {i < words.length - 1 && " "}
        </Fragment>
      ))}
    </>
  );
}
