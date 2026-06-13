// Root router — wires all page routes for Salone Explorer.
import { Routes, Route } from "react-router-dom";
import HomePage from "@/pages/HomePage";
import AttractionDetailPage from "@/pages/AttractionDetailPage";
import AboutPage from "@/pages/AboutPage";
import NotFoundPage from "@/pages/NotFoundPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/attractions/:id" element={<AttractionDetailPage />} />
      <Route path="/about" element={<AboutPage />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
