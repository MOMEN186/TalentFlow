import { useContext, useEffect, useState } from "react";
import { AuthContext } from "../contexts/AuthContext";
import useAxios from "../utils/useAxios";
import { cookies } from "../utils/cookies";
import { Table, Button } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import { FaSignOutAlt, FaUserCircle } from "react-icons/fa"; // ✅ استيراد أيقونة المستخدم

function Profile() {
    const navigate = useNavigate();
    const { image, setImage, setUser } = useContext(AuthContext);
    const api = useAxios();
    const [employeeData, setEmployeeData] = useState(null);

    async function uploadFile(formData) {
        try {
            const response = await api.post(
                "api/auth/profile/upload_photo/",
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

    const handleLogout = async () => {
        try {
            const refreshToken = cookies.get("refresh_token");
            if (refreshToken) {
                await api.post("api/auth/logout/", { refresh: refreshToken });
            }
            setUser(null);
            cookies.remove("access_token");
            cookies.remove("refresh_token");
            navigate("/login");
        } catch (err) {
            console.error("Logout failed:", err);
            alert("Logout failed. Please try again.");
        }
    };

    useEffect(() => {
        const getProfileData = async () => {
            try {
                const response = await api.get("api/auth/profile/me/");
                if (response.data.employee_data) {
                    setEmployeeData(response.data.employee_data);
                }
            } catch (err) {
                console.error("Failed to fetch profile:", err);
            }
        };
        getProfileData();
    }, []);

    return (
        <div style={{ padding: "40px", maxWidth: "700px", margin: "auto" }}>
            <div className="profile-container d-flex flex-column align-items-center">
                <div
                    style={{ position: "relative", width: 200, height: 200 }}
                    className="profile-photo-container mb-4"
                >
                    {/* ✅ الكود الشرطي الجديد */}
                    {image ? (
                        <img
                            src={image}
                            alt="Profile"
                            style={{
                                width: "100%",
                                height: "100%",
                                borderRadius: "50%",
                                objectFit: "cover",
                                boxShadow: "0px 4px 15px rgba(0, 0, 0, 0.1)",
                            }}
                        />
                    ) : (
                        <div
                            style={{
                                width: "100%",
                                height: "100%",
                                borderRadius: "50%",
                                display: "flex",
                                justifyContent: "center",
                                alignItems: "center",
                                backgroundColor: "#f0f2f5", // لون رمادي فاتح للخلفية
                                boxShadow: "0px 4px 15px rgba(0, 0, 0, 0.1)",
                            }}
                        >
                            <FaUserCircle style={{ fontSize: "150px", color: "#ccc" }} />
                        </div>
                    )}
                    {/* ✅ نهاية الكود الشرطي */}
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
                            border: "2px dashed #fff",
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
                </div>
                <h1 className="text-primary mb-2">
                    {employeeData?.first_name} {employeeData?.last_name}
                </h1>
                <p className="text-muted">{employeeData?.job_title?.name || "Job Title"}</p>
            </div>
            <hr className="my-4" />
            {employeeData && (
                <Table className="profile-table">
                    <tbody>
                        <tr>
                            <td className="table-header">Email</td>
                            <td className="table-data">{employeeData.email}</td>
                        </tr>
                        <tr>
                            <td className="table-header">Phone</td>
                            <td className="table-data">{employeeData.phone}</td>
                        </tr>
                        <tr>
                            <td className="table-header">Department</td>
                            <td className="table-data">{employeeData.department?.name || "N/A"}</td>
                        </tr>
                        <tr>
                            <td className="table-header">Job Title</td>
                            <td className="table-data">{employeeData.job_title?.name || "N/A"}</td>
                        </tr>
                        <tr>
                            <td className="table-header">Address</td>
                            <td className="table-data">{employeeData.address || "N/A"}</td>
                        </tr>
                        <tr>
                            <td className="table-header">Date of Birth</td>
                            <td className="table-data">{employeeData.date_of_birth || "N/A"}</td>
                        </tr>
                        <tr>
                            <td className="table-header">Hire Date</td>
                            <td className="table-data">{employeeData.date_joined || "N/A"}</td>
                        </tr>
                    </tbody>
                </Table>
            )}
            <div className="d-flex justify-content-center mt-4">
                <Button variant="danger" onClick={handleLogout} className="logout-btn">
                    <FaSignOutAlt className="me-2" /> Logout
                </Button>
            </div>
            <style>
                {`
                .profile-container {
                    text-align: center;
                }
                .profile-table {
                    border: none !important;
                }
                .profile-table td {
                    border: none !important;
                    padding: 12px 0;
                }
                .table-header {
                    font-weight: bold;
                    color: #495057;
                    width: 30%;
                }
                .table-data {
                    text-align: right;
                }
                .logout-btn {
                    padding: 10px 30px;
                    border-radius: 50px;
                }
                .hover-overlay:hover {
                    opacity: 1 !important;
                }
                `}
            </style>
        </div>
    );
}

export default Profile;