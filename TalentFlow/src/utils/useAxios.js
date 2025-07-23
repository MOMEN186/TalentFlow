
import { useContext } from "react";
import { AuthContext } from "../contexts/AuthContext";
import dayjs from "dayjs";
import { jwtDecode } from "jwt-decode";
import axios from "axios";

const useAxios = () => {
    const { authTokens, setUser, setAuthTokens } = useContext(AuthContext); 

    const axiosInstance = axios.create({
      baseURL: "http://127.0.0.1:8000/api",
      headers: {
        Authorization: `Bearer ${authTokens.access}`,
      },
    });
  
async function TokenInterceptor(req) {
  const user = jwtDecode(authTokens.access);
  const isExpired = dayjs.unix(user.exp).diff(dayjs()) < 1;
  console.log("isExpired", isExpired);
  if (!isExpired) return req;

  const res = await axios.post("http://localhost:8000/api/auth/refresh/", {
    refresh: authTokens.refresh,
    access: authTokens.access,
  });
        setAuthTokens(res.data);
        setUser(jwtDecode(res.data.access));

  req.headers.Authorization = `Bearer ${res.data.access}`;
  return req;
}

  axiosInstance.interceptors.request.use(TokenInterceptor);
  
  return axiosInstance;
}

export default useAxios;
