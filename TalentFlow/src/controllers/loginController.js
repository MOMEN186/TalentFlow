import { api } from "../api/api.js";

const port = 8000;
const host = "http://127.0.0.1";
const auth = `${host}:${port}/api/auth`;//auth api

export async function login(email, password) {
    try {
    const res = await api({
      method: "POST",
      url: `${auth}/login/`,
      data: {
        email,
        password,
      },
    });
    const data = res.data;
    console.log(data);
    return data;
  } catch (error) {
    console.error("Login failed:", error.response?.data || error.message);
    throw error;
  }
}

export async function logout(email,password,token) {
    try {
        const res = await api({
            method: "POST",
            url: `${auth}/logout/`,
            data: {
                email,
                password,
                token
            },
        });
        const data = await res.data;
        return data;
    }
    catch (e) {
        console.log(e);
    }
}
