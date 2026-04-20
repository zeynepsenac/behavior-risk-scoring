export default function ErrorBox({ message }) {
  return (
    <div style={{
      padding: "30px",
      color: "#dc2626",
      fontWeight: "600"
    }}>
      ❌ Hata: {message}
    </div>
  );
}