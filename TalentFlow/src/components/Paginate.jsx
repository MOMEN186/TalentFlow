import React, { useEffect, useState } from "react";
import Pagination from "react-bootstrap/Pagination";
import { useNavigate, useLocation } from "react-router-dom";

function Paginate({ page, totalPages }) {
  const [pageNumbers, setPageNumbers] = useState([1]);
  const navigate = useNavigate();
  const location = useLocation();

  const goTo = (i) => {
    if (i >= 1 && i <= totalPages) {
      // strip trailing /number if it exists
      const basePath = location.pathname.replace(/\/\d+$/, "");
      // if already at base (like "/employees"), use it directly
      const target = basePath === location.pathname ? `${basePath}/${i}` : `${basePath}/${i}`;
      navigate(target);
    }
  };

  const pageWindowSize = 9;

  useEffect(() => {
    const arr = [];
    for (let i = page; i <= page + pageWindowSize && i <= totalPages; i++) {
      arr.push(i);
    }
    setPageNumbers(arr);
  }, [page, totalPages]);

  return (
    <Pagination className="justify-content-center mt-3">
      <Pagination.First onClick={() => goTo(1)} disabled={page === 1} />
      <Pagination.Prev onClick={() => goTo(page - 1)} disabled={page === 1} />

      {pageNumbers.map((num) => (
        <Pagination.Item
          key={num}
          active={num === page}
          onClick={() => goTo(num)}
        >
          {num}
        </Pagination.Item>
      ))}

      <Pagination.Next onClick={() => goTo(page + 1)} disabled={page === totalPages} />
      <Pagination.Last onClick={() => goTo(totalPages)} disabled={page === totalPages} />
    </Pagination>
  );
}

export default Paginate;
