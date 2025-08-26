// في ملف Paginate.jsx
import React, { useEffect, useState } from "react";
import Pagination from "react-bootstrap/Pagination";

// ✅ استقبل setPage كخاصية
function Paginate({ page, totalPages, setPage }) {
  const [pageNumbers, setPageNumbers] = useState([1]);

  const goTo = (i) => {
    if (i >= 1 && i <= totalPages) {
      // ✅ استدعي setPage مباشرة لتغيير الحالة
      setPage(i);
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