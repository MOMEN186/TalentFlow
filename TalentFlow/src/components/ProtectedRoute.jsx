import { useContext } from 'react'
import { Navigate } from 'react-router-dom';
import { AuthContext } from "../contexts/AuthContext";
function ProtectedRoute({element }) {
  const { authTokens } = useContext(AuthContext);
  return authTokens?.access ? element : <Navigate to={'/login'} />;
}

export default ProtectedRoute