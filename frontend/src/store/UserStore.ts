import { create } from "zustand";
import axios from "axios";

interface UserProps {
    username: string;
    password: string;
}

interface UserStore {
    users: UserProps[];
    register: (data: UserProps) => Promise<void>;
    authLogin: (data: UserProps) => Promise<void>;
}

const useUserStore = create<UserStore>((set) => ({
    users: [],
    register: async (data: UserProps) => {
        try {
            const response = await axios.post("http://127.0.0.1:5000/api/users", data);
            set((state) => ({
                users: [...state.users, response.data] // Update the state with the new user
            }));
        } catch (error) {
            console.error("Error registering user:", error);
        }
    },
    authLogin: async (data: UserProps) => {
        try {
            const response = await axios.post("http://127.0.0.1:5000/api/login", data);
            // Assume the response contains user data
            set(() => ({
                users: [response.data] // Store user data on successful login
            }));
            console.log("Login successful:", response.data);
        } catch (error) {
            console.error("Error logging in:", error);
            throw error; // Rethrow to handle in the component
        }
    }
    
}));

export default useUserStore;
