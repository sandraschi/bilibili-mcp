import { Route, Routes } from "react-router-dom";
import Layout from "./Layout";
import Chat from "./pages/Chat";
import Dashboard from "./pages/Dashboard";
import Explore from "./pages/Explore";
import Help from "./pages/Help";
import Inbox from "./pages/Inbox";
import Logs from "./pages/Logs";
import Search from "./pages/Search";
import Settings from "./pages/Settings";
import Skills from "./pages/Skills";
import Tools from "./pages/Tools";
import Video from "./pages/Video";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/explore" element={<Explore />} />
        <Route path="/search" element={<Search />} />
        <Route path="/video" element={<Video />} />
        <Route path="/tools" element={<Tools />} />
        <Route path="/skills" element={<Skills />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/inbox" element={<Inbox />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/logs" element={<Logs />} />
        <Route path="/help" element={<Help />} />
      </Route>
    </Routes>
  );
}
