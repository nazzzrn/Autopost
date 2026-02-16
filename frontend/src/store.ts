import { create } from 'zustand';
import axios from 'axios';

interface WorkflowState {
    topic: string;
    platforms: string[];
    captions: Record<string, string>;
    image_path: string | null;
    schedule_time: string | null;
    publish_status: Record<string, string | undefined>;
    feedback: string;
    regenerate_count_caption: number;
    regenerate_count_image: number;
    current_step: string;
    isLoading: boolean;
    error: string | null;

    // Actions
    startWorkflow: (prompt: string) => Promise<void>;
    fetchState: () => Promise<void>;
    reviewCaption: (accepted: boolean, feedback?: string, captions?: Record<string, string>) => Promise<void>;
    reviewImage: (accepted: boolean, feedback?: string, imagePath?: string) => Promise<void>;
    schedule: (time: string) => Promise<void>;
    publish: () => Promise<void>;
}

const API_URL = 'http://localhost:8000';

export const useWorkflowStore = create<WorkflowState>((set) => ({
    topic: "",
    platforms: [],
    captions: {},
    image_path: null,
    schedule_time: null,
    publish_status: {},
    feedback: "",
    regenerate_count_caption: 0,
    regenerate_count_image: 0,
    current_step: "prompt",
    isLoading: false,
    error: null,

    startWorkflow: async (prompt: string) => {
        set({ isLoading: true, error: null });
        try {
            const res = await axios.post(`${API_URL}/workflow/start`, { prompt });
            set({ ...res.data, isLoading: false });
        } catch (err: any) {
            set({ error: err.message, isLoading: false });
        }
    },

    fetchState: async () => {
        set({ isLoading: true, error: null });
        try {
            const res = await axios.get(`${API_URL}/workflow/state`);
            set({ ...res.data, isLoading: false });
        } catch (err: any) {
            set({ error: err.message, isLoading: false });
        }
    },

    reviewCaption: async (accepted: boolean, feedback?: string, captions?: Record<string, string>) => {
        set({ isLoading: true, error: null });
        try {
            const res = await axios.post(`${API_URL}/workflow/review-caption`, {
                accepted,
                feedback,
                captions: captions || {} // Ensure captions are passed back if edited
            });
            set({ ...res.data, isLoading: false });
        } catch (err: any) {
            set({ error: err.response?.data?.detail || err.message, isLoading: false });
        }
    },

    reviewImage: async (accepted: boolean, feedback?: string, imagePath?: string) => {
        set({ isLoading: true, error: null });
        try {
            const res = await axios.post(`${API_URL}/workflow/review-image`, {
                accepted,
                feedback,
                image_path: imagePath
            });
            set({ ...res.data, isLoading: false });
        } catch (err: any) {
            set({ error: err.response?.data?.detail || err.message, isLoading: false });
        }
    },

    schedule: async (time: string) => {
        set({ isLoading: true, error: null });
        try {
            const res = await axios.post(`${API_URL}/workflow/schedule`, { schedule_time: time });
            set({ ...res.data, isLoading: false });
        } catch (err: any) {
            set({ error: err.message, isLoading: false });
        }
    },

    publish: async () => {
        set({ isLoading: true, error: null });
        try {
            const res = await axios.post(`${API_URL}/workflow/publish`);
            set({ ...res.data, isLoading: false });
        } catch (err: any) {
            set({ error: err.message, isLoading: false });
        }
    }
}));
