import { create } from 'zustand';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

interface AnalyticsOverview {
    total_reach: number;
    total_impressions: number;
    avg_engagement_rate: number;
    total_posts_tracked: number;
}

interface AnalyticsEntry {
    id: string;
    post_id: string;
    reach: number;
    impressions: number;
    engagement: number;
    likes: number;
    comments: number;
    engagement_rate: number;
    fetched_at: string;
    post?: {
        id: string;
        platform: string;
        caption: string;
        image_url: string | null;
        status: string;
        scheduled_time: string | null;
        published_time: string | null;
    };
}

interface PlatformInsights {
    facebook: Record<string, any>;
    instagram: Record<string, any>;
    message: string;
}

interface AnalyticsState {
    overview: AnalyticsOverview | null;
    postAnalytics: AnalyticsEntry[];
    timeseries: AnalyticsEntry[];
    platformInsights: PlatformInsights | null;
    isLoading: boolean;
    error: string | null;

    fetchOverview: () => Promise<void>;
    fetchPostAnalytics: () => Promise<void>;
    fetchTimeseries: () => Promise<void>;
    refreshData: () => Promise<void>;
    deletePost: (postId: string) => Promise<void>;
}

export const useAnalyticsStore = create<AnalyticsState>((set) => ({
    overview: null,
    postAnalytics: [],
    timeseries: [],
    platformInsights: null,
    isLoading: false,
    error: null,

    fetchOverview: async () => {
        set({ isLoading: true, error: null });
        try {
            const res = await axios.get(`${API_URL}/analytics/overview`);
            set({ overview: res.data, isLoading: false });
        } catch (err: any) {
            set({ error: err.response?.data?.detail || err.message, isLoading: false });
        }
    },

    fetchPostAnalytics: async () => {
        set({ isLoading: true, error: null });
        try {
            const res = await axios.get(`${API_URL}/analytics/posts`);
            set({ postAnalytics: res.data, isLoading: false });
        } catch (err: any) {
            set({ error: err.response?.data?.detail || err.message, isLoading: false });
        }
    },

    fetchTimeseries: async () => {
        set({ isLoading: true, error: null });
        try {
            const res = await axios.get(`${API_URL}/analytics/insights`);
            set({ timeseries: res.data, isLoading: false });
        } catch (err: any) {
            set({ error: err.response?.data?.detail || err.message, isLoading: false });
        }
    },

    refreshData: async () => {
        set({ isLoading: true, error: null });
        try {
            const res = await axios.post(`${API_URL}/analytics/refresh`);
            set({ platformInsights: res.data, isLoading: false });
        } catch (err: any) {
            set({ error: err.response?.data?.detail || err.message, isLoading: false });
        }
    },

    deletePost: async (postId: string) => {
        set({ isLoading: true, error: null });
        try {
            await axios.delete(`${API_URL}/analytics/posts/${postId}`);
            set((state) => ({
                postAnalytics: state.postAnalytics.filter(p => p.post_id !== postId),
                isLoading: false
            }));
        } catch (err: any) {
            set({ error: err.response?.data?.detail || err.message, isLoading: false });
        }
    },
}));
