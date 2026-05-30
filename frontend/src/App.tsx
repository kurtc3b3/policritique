import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { Layout } from "./components/Layout";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { AuthProvider } from "./contexts/AuthContext";
import { ConstituenciesPage } from "./pages/ConstituenciesPage";
import { ElectionsPage } from "./pages/ElectionsPage";
import { HomePage } from "./pages/HomePage";
import { LoginPage } from "./pages/LoginPage";
import { ManifestoDetailPage } from "./pages/ManifestoDetailPage";
import { ManifestosPage } from "./pages/ManifestosPage";
import { MemberDetailPage } from "./pages/MemberDetailPage";
import { MembersPage } from "./pages/MembersPage";
import { PartiesPage } from "./pages/PartiesPage";
import { RegisterPage } from "./pages/RegisterPage";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route element={<ProtectedRoute />}>
            <Route element={<Layout />}>
              <Route path="/" element={<HomePage />} />
              <Route path="/elections" element={<ElectionsPage />} />
              <Route path="/members" element={<MembersPage />} />
              <Route path="/members/:memberId" element={<MemberDetailPage />} />
              <Route path="/parties" element={<PartiesPage />} />
              <Route path="/constituencies" element={<ConstituenciesPage />} />
              <Route path="/manifestos" element={<ManifestosPage />} />
              <Route path="/manifestos/:manifestoId" element={<ManifestoDetailPage />} />
            </Route>
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
