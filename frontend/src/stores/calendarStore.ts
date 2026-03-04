import { create } from 'zustand';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

export interface CalendarPost {
    id: string;
    user_id: string | null;
    platform: string;
    caption: string;
    image_url: string | null;
    status: string;
    scheduled_time: string | null;
    published_time: string | null;
    created_at: string;
    updated_at: string;
}

interface CalendarState {
    posts: CalendarPost[];
    isLoading: boolean;
    error: string | null;

    fetchPosts: (status?: string) => Promise<void>;
    createPost: (data: {
        platform: string;
        caption: string;
        image_url?: string;
        status?: string;
        scheduled_time?: string;
    }) => Promise<void>;
    updatePost: (id: string, data: {
        caption?: string;
        image_url?: string;
        status?: string;
        scheduled_time?: string;
    }) => Promise<void>;
    deletePost: (id: string) => Promise<void>;
}

export const useCalendarStore = create<CalendarState>((set) => ({
    posts: [],
    isLoading: false,
    error: null,

    fetchPosts: async (status?: string) => {
        set({ isLoading: true, error: null });
        try {
            const params = status ? { status } : {};
            const res = await axios.get(`${API_URL}/posts`, { params });
            set({ posts: res.data, isLoading: false });
        } catch (err: any) {
            set({ error: err.response?.data?.detail || err.message, isLoading: false });
        }
    },

    createPost: async (data) => {
        set({ isLoading: true, error: null });
        try {
            await axios.post(`${API_URL}/posts`, data);
            // Refresh list
            const res = await axios.get(`${API_URL}/posts`);
            set({ posts: res.data, isLoading: false });
        } catch (err: any) {
            set({ error: err.response?.data?.detail || err.message, isLoading: false });
        }
    },

    updatePost: async (id, data) => {
        set({ isLoading: true, error: null });
        try {
            await axios.put(`${API_URL}/posts/${id}`, data);
            // Refresh list
            const res = await axios.get(`${API_URL}/posts`);
            set({ posts: res.data, isLoading: false });
        } catch (err: any) {
            set({ error: err.response?.data?.detail || err.message, isLoading: false });
        }
    },

    deletePost: async (id) => {
        set({ isLoading: true, error: null });
        try {
            await axios.delete(`${API_URL}/posts/${id}`);
            const res = await axios.get(`${API_URL}/posts`);
            set({ posts: res.data, isLoading: false });
        } catch (err: any) {
            set({ error: err.response?.data?.detail || err.message, isLoading: false });
        }
    },
}));
