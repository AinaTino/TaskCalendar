// src/store/UserStore.ts

import { create } from "zustand";
import axios from "axios";
import { setCookie, removeCookie } from '@/utils/cookieUtils'; // Import removeCookie

interface UserProps {
    username: string;
    password: string;
}

interface UserStore {
    users: UserProps[];
    register: (data: UserProps) => Promise<void>;
    authLogin: (data: UserProps) => Promise<any>;
    logout: () => void; // Add logout method
}

const useUserStore = create<UserStore>((set) => ({
    users: [],
    register: async (data: UserProps) => {
        try {
            const response = await axios.post("http://127.0.0.1:5000/api/users", data);
            set((state) => ({
                users: [...state.users, response.data]
            }));
        } catch (error) {
            console.error("Error registering user:", error);
        }
    },
    authLogin: async (data: UserProps) => {
        try {
            const response = await axios.post("http://127.0.0.1:5000/api/login", data);
            const token = response.data.token;
            if (token) {
                setCookie('authToken', token, 7); // Set the token in the cookie for 7 days
                console.log('Token set:', token); // Debugging line
            }
            return response;
        } catch (error) {
            console.error("Error logging in:", error);
            throw error;
        }
    },
    logout: () => {
        removeCookie('authToken'); // Clear the token from cookies
        console.log('Logged out and token removed'); // Debugging line
    }
}));

export default useUserStore;
