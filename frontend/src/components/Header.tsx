// src/components/Header.tsx (example component)

import React from 'react';
import { Link } from 'react-router-dom';
import useUserStore from '@/store/UserStore';

const Header: React.FC = () => {
    const logout = useUserStore((state) => state.logout);

    return (
        <header className="bg-gray-800 p-4 text-white">
            <nav>
                <Link to="/" className="mr-4">Home</Link>
                <Link to="/profile" className="mr-4">Profile</Link>
                <button
                    onClick={() => {
                        logout(); // Call logout method
                        window.location.href = '/login'; // Redirect to login page after logout
                    }}
                    className="bg-red-600 px-4 py-2 rounded"
                >
                    Logout
                </button>
            </nav>
        </header>
    );
};

export default Header;
