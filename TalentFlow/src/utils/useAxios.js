import { useContext, useEffect, useRef, useMemo } from "react";
import { AuthContext } from "../contexts/AuthContext";
import dayjs from "dayjs";
import { jwtDecode } from "jwt-decode";
import axios from "axios";
import { cookies } from "./cookies";

const API_BASE = "http://127.0.0.1:8000"; // keep consistent

const useAxios = () => {
  const { authTokens, setUser, setAuthTokens } = useContext(AuthContext);

  // create axios instance once
  const axiosInstance = useMemo(() => {
    return axios.create({
      baseURL: API_BASE,
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // refs to avoid stale closures
  const authRef = useRef(authTokens);
  useEffect(() => {
    authRef.current = authTokens;
  }, [authTokens]);

  // refresh control
  const isRefreshing = useRef(false);
  const failedQueue = useRef([]); // { resolve, reject }

  const processQueue = (error, token = null) => {
    failedQueue.current.forEach(({ resolve, reject }) => {
      if (error) reject(error);
      else resolve(token);
    });
    failedQueue.current = [];
  };

  useEffect(() => {
    const interceptorId = axiosInstance.interceptors.request.use(
      async (req) => {
        // attach access token if present
        const tokens = authRef.current;
        if (!tokens) return req;

        // If no access token on header, set it
        console.log(tokens.access)
        if (tokens.access) req.headers.Authorization = `Bearer ${tokens.access}`;

        // decode to check expiration
        try {
          const user =  jwtDecode (tokens.access);
          const isExpired = dayjs.unix(user.exp).diff(dayjs()) < 1;
          if (!isExpired) return req;
        // eslint-disable-next-line no-unused-vars
        } catch (e) {
          // If decode fails, try refreshing
        }

        // If token expired, attempt refresh
        if (isRefreshing.current) {
          // wait for the ongoing refresh
          return new Promise((resolve, reject) => {
            failedQueue.current.push({
              resolve: (token) => {
                req.headers.Authorization = `Bearer ${token}`;
                resolve(req);
              },
              reject,
            });
          });
        }

        isRefreshing.current = true;

        try {
          const refreshToken = authRef.current?.refresh;
          if (!refreshToken) throw new Error("No refresh token");

          // call refresh endpoint (use axios, not axiosInstance to avoid loops)
          const res = await axios.post(
            `${API_BASE}/api/auth/refresh/`,
            { refresh: refreshToken },
            { headers: { "Content-Type": "application/json" } }
          );

          const newAccess = res.data.access;
          const newRefresh = res.data.refresh ?? refreshToken; // replace if backend returned refresh

          const newTokens = { access: newAccess, refresh: newRefresh };

          // persist tokens in your app state + cookie/localStorage
          setAuthTokens(newTokens);
          cookies.set("authTokens", newTokens); // adapt to your cookies helper
          setUser( jwtDecode (newAccess));

          processQueue(null, newAccess);

          req.headers.Authorization = `Bearer ${newAccess}`;
          return req;
        } catch (err) {
          processQueue(err, null);
          // cleanup and force login
          setAuthTokens(null);
          setUser(null);
          cookies.remove("authTokens");
          window.location.href = "/login";
          return Promise.reject(err);
        } finally {
          isRefreshing.current = false;
        }
      },
      (error) => Promise.reject(error)
    );

    // cleanup on unmount
    return () => {
      axiosInstance.interceptors.request.eject(interceptorId);
    };
    // only run once
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [axiosInstance, setAuthTokens, setUser]);

  return axiosInstance;
};

export default useAxios;
