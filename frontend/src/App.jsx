import "./App.css";
import UserInfo from "./components/auth/UserInfo";

function App() {
  return (
    <div
      className="App"
      style={{
        minHeight: "100vh",
        backgroundColor: "#f5f5f5",
      }}
    >
      <UserInfo />
    </div>
  );
}

export default App;
