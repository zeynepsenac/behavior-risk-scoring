import { useEffect, useState } from "react";

function TypingText({ text, speed = 20 }) {
  const [displayed, setDisplayed] = useState("");

  useEffect(() => {
    let i = 0;

    const interval = setInterval(() => {
      setDisplayed(text.slice(0, i));
      i++;

      if (i > text.length) {
        clearInterval(interval);
      }
    }, speed);

    return () => clearInterval(interval);
  }, [text, speed]);

  return (
    <span className="typing-text">
      {displayed}
      <span className="cursor"></span>
    </span>
  );
}

export default TypingText;