import React, { useEffect } from 'react'
import useAxios from '../utils/useAxios';

function Payroll() {

  const api = useAxios();
  useEffect(() => {
    const get = async () => await api("http://localhost:8000/api/payroll/");
    get();
  }, []);
  return (
    <div>Payroll</div>
  )
}

export default Payroll