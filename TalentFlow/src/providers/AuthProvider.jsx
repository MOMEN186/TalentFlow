// src/providers/AuthProvider.jsx - CORRECTED VERSION
import { useEffect, useState } from "react";
import { AuthContext } from "../contexts/AuthContext";
import { cookies } from "../utils/cookies";
import { jwtDecode } from "jwt-decode";
import { useNavigate } from "react-router-dom";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => cookies.get("user") || null);
  const [authTokens, setAuthTokens] = useState(
    () => cookies.get("authTokens") || null
  );
  const [image, setImage] = useState("https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png");
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    if (authTokens) {
      setUser(jwtDecode(authTokens.access));
    }
    setLoading(false);
  }, [authTokens, loading]);

  useEffect(() => {
  setImage(cookies.get("profile_photo"))
},[])


  const login = async (email, password) => {
    const baseURL = import.meta.env.VITE_API_BASE;
    console.log(baseURL)
    let response = await fetch(`${baseURL}/api/auth/login/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email,
        password,
      }),
    });
    let data = await response.json();

    if (response.status === 200) {
      setAuthTokens(data);
      setUser(jwtDecode(data.access));
      cookies.set("authTokens", data);
      navigate("/");
    } else {
      alert("Something went wrong!");
    }
  };

  return (
    <AuthContext.Provider
      value={{ user, setUser, authTokens, setAuthTokens, login ,image,setImage}}
    >
      {children}
    </AuthContext.Provider>
  );
}
