import { useState } from "react";
import "./App.css";
import UserInfo from "./components/auth/UserInfo";
import Chat from "./components/chat/Chat";

function App() {
  const [user, setUser] = useState(null); // Track user login state

  return (
    <div
      className="App"
      style={{
        minHeight: "100vh",
        backgroundColor: "#f5f5f5",
        padding: "20px",
      }}
    >
      <UserInfo onUserChange={setUser} />

      {user ? (
        // Show chat only when user is logged in
        <div style={{ marginTop: "40px" }}>
          <h2
            style={{ textAlign: "center", marginBottom: "20px", color: "#333" }}
          >
            AI Chat Assistant
          </h2>
          <Chat />
        </div>
      ) : (
        <div></div>
      )}
    </div>
  );
}

export default App;
