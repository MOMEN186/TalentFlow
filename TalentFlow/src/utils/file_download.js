export const handleDownload = async (api,target) => {
    
    try {
      const res = await api.get(`/${target}/export/?excel=true`, {
        responseType: "blob",  // correct spelling
      });

      // Build a Blob and trigger a download
      const blob = new Blob([res.data], {
        type: res.headers["content-type"] ||
              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;

      // Try to extract filename from headers, fallback if absent
      const disposition = res.headers["content-disposition"];
      let fileName = `${target}.xlsx`;
      if (disposition) {
        const match = disposition.match(/filename="(.+)"/);
        if (match) fileName = match[1];
      }
      a.download = fileName;

      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

    } catch (err) {
      console.error("Download failed:", err);
    }
  };