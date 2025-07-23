import { useContext } from "react";
import { AuthContext } from "../contexts/AuthContext";
import useAxios from "../utils/useAxios";
import { cookies } from "../utils/cookies";

function Profile() {
  
  const { image,setImage } = useContext(AuthContext);
  const api = useAxios();


  async function uploadFile(formData) {
     try {
      const response = await api.post(
        "auth/profile_photo/",
        formData,
        {
          withCredentials: true,
          headers: { "Content-Type": "multipart/form-data" },
        }
      );
      return response.data;
    } catch (err) {
      console.error("Upload failed:", err.response?.data || err.message);
      throw err;
    }
  }

  const handleImageChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setImage(file);

    const reader = new FileReader();
    reader.onloadend = () => setImage(reader.result);
    reader.readAsDataURL(file);

    const formData = new FormData();
    formData.append("image", file);
    const res = await uploadFile(formData);
    setImage(res.photo_url);
    cookies.set("profile_photo", res.photo_url);
  

  };

  return (
    <div
      style={{ position: "relative", width: 200, height: 200, margin: "auto" }}
    >
      <img
        src={image}
        alt="Profile"
        style={{
          width: "100%",
          height: "100%",
          borderRadius: "50%",
          objectFit: "cover",
        }}
      />

      {/* Overlay Input */}
      <label
        htmlFor="imageUpload"
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          backgroundColor: "rgba(0,0,0,0.4)",
          color: "#fff",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          borderRadius: "50%",
          opacity: 0,
          cursor: "pointer",
          transition: "opacity 0.3s",
        }}
        className="hover-overlay"
      >
        Upload
        <input
          id="imageUpload"
          type="file"
          accept="image/*"
          onChange={handleImageChange}
          style={{ display: "none" }}
        />
      </label>

      {/* Hover effect using inline style or CSS */}
      <style>
        {`
          .hover-overlay:hover {
            opacity: 1 !important;
          }
        `}
      </style>
    </div>
  );
}

export default Profile;
