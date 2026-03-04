import React, { useEffect } from 'react';
import { useAnalyticsStore } from '../stores/analyticsStore';
import {
    LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
    Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import {
    BarChart3, TrendingUp, Eye, Activity, RefreshCw, Loader2,
    Award, Instagram, Facebook
} from 'lucide-react';

const KPICard: React.FC<{
    title: string;
    value: string | number;
    icon: React.ReactNode;
    subtitle?: string;
}> = ({ title, value, icon, subtitle }) => (
    <div className="glass-card p-6 group hover:border-brand/30 transition-all duration-500 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-32 h-32 bg-brand/5 blur-3xl rounded-full -translate-y-1/2 translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none" />
        <div className="relative z-10">
            <div className="flex items-center justify-between mb-4">
                <span className="text-[10px] font-bold uppercase tracking-[0.3em] text-gray-500">{title}</span>
                <div className="w-10 h-10 rounded-xl bg-brand/10 border border-brand/20 flex items-center justify-center text-brand">
                    {icon}
                </div>
            </div>
            <div className="text-3xl font-black text-white tracking-tight">{value}</div>
            {subtitle && <p className="text-xs text-gray-500 mt-2 font-medium">{subtitle}</p>}
        </div>
    </div>
);

const customTooltipStyle = {
    backgroundColor: 'rgba(10, 25, 25, 0.95)',
    border: '1px solid rgba(20, 50, 50, 0.6)',
    borderRadius: '12px',
    padding: '12px 16px',
    boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
};

const DashboardPage: React.FC = () => {
    const {
        overview, postAnalytics, timeseries, platformInsights,
        isLoading, error,
        fetchOverview, fetchPostAnalytics, fetchTimeseries, refreshData
    } = useAnalyticsStore();

    useEffect(() => {
        fetchOverview();
        fetchPostAnalytics();
        fetchTimeseries();
    }, []);

    const bestPost = postAnalytics.length > 0
        ? postAnalytics.reduce((best, curr) =>
            curr.engagement_rate > best.engagement_rate ? curr : best
        )
        : null;

    // Prepare chart data
    const chartData = timeseries.map(t => ({
        date: t.fetched_at ? new Date(t.fetched_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : '',
        impressions: t.impressions,
        reach: t.reach,
        engagement: t.engagement,
    }));

    const barData = postAnalytics.map(pa => ({
        name: pa.post?.caption?.substring(0, 20) || pa.post_id.substring(0, 8),
        reach: pa.reach,
        impressions: pa.impressions,
        platform: pa.post?.platform || 'unknown',
    }));

    return (
        <div className="min-h-screen bg-pixora-bg">
            {/* Header */}
            <div className="mb-8 flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-brand/10 border border-brand/20 flex items-center justify-center text-brand">
                        <BarChart3 size={24} />
                    </div>
                    <div>
                        <h2 className="text-3xl font-bold text-white tracking-tight">Analytics Dashboard</h2>
                        <p className="text-gray-500 text-sm mt-1 font-medium">Performance insights across your platforms</p>
                    </div>
                </div>
                <button
                    onClick={async () => {
                        await refreshData();
                        await fetchOverview();
                        await fetchPostAnalytics();
                        await fetchTimeseries();
                    }}
                    disabled={isLoading}
                    className="pixora-btn-secondary flex items-center gap-2"
                >
                    {isLoading ? <Loader2 className="animate-spin" size={18} /> : <RefreshCw size={18} />}
                    <span>REFRESH</span>
                </button>
            </div>

            {error && (
                <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl text-sm">
                    {error}
                </div>
            )}

            {/* Platform API Data */}
            {platformInsights && (
                <div className="mb-8 glass-card p-6 border-brand/10">
                    <h3 className="text-xs font-bold uppercase tracking-[0.3em] text-gray-500 mb-4">Live Platform Data</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="p-4 rounded-xl bg-pixora-darker-green/50 border border-pixora-border">
                            <div className="flex items-center gap-2 mb-3">
                                <Facebook size={16} className="text-blue-400" />
                                <span className="text-xs font-bold uppercase tracking-widest text-blue-400">Facebook</span>
                            </div>
                            {platformInsights.facebook.error ? (
                                <p className="text-gray-500 text-xs">{platformInsights.facebook.error}</p>
                            ) : (
                                <div className="space-y-1">
                                    {Object.entries(platformInsights.facebook).map(([k, v]) => (
                                        <div key={k} className="flex justify-between text-xs">
                                            <span className="text-gray-400">{k.replace(/_/g, ' ')}</span>
                                            <span className="text-white font-mono">{String(v)}</span>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                        <div className="p-4 rounded-xl bg-pixora-darker-green/50 border border-pixora-border">
                            <div className="flex items-center gap-2 mb-3">
                                <Instagram size={16} className="text-pink-400" />
                                <span className="text-xs font-bold uppercase tracking-widest text-pink-400">Instagram</span>
                            </div>
                            {platformInsights.instagram.error ? (
                                <p className="text-gray-500 text-xs">{platformInsights.instagram.error}</p>
                            ) : (
                                <div className="space-y-1">
                                    {Object.entries(platformInsights.instagram).map(([k, v]) => (
                                        <div key={k} className="flex justify-between text-xs">
                                            <span className="text-gray-400">{k.replace(/_/g, ' ')}</span>
                                            <span className="text-white font-mono">{String(v)}</span>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                <KPICard
                    title="Total Reach"
                    value={overview?.total_reach?.toLocaleString() || '0'}
                    icon={<Eye size={20} />}
                    subtitle="Across all tracked posts"
                />
                <KPICard
                    title="Total Impressions"
                    value={overview?.total_impressions?.toLocaleString() || '0'}
                    icon={<TrendingUp size={20} />}
                    subtitle="Total content views"
                />
                <KPICard
                    title="Avg Engagement"
                    value={`${overview?.avg_engagement_rate?.toFixed(1) || '0'}%`}
                    icon={<Activity size={20} />}
                    subtitle="Engagement rate average"
                />
                <KPICard
                    title="Posts Tracked"
                    value={overview?.total_posts_tracked || 0}
                    icon={<BarChart3 size={20} />}
                    subtitle="With analytics data"
                />
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                {/* Line Chart — Impressions over time */}
                <div className="glass-card p-6">
                    <h3 className="text-xs font-bold uppercase tracking-[0.3em] text-gray-500 mb-6">Impressions Over Time</h3>
                    {chartData.length > 0 ? (
                        <ResponsiveContainer width="100%" height={280}>
                            <LineChart data={chartData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(20,50,50,0.4)" />
                                <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#6B7280' }} />
                                <YAxis tick={{ fontSize: 10, fill: '#6B7280' }} />
                                <Tooltip contentStyle={customTooltipStyle} labelStyle={{ color: '#9CA3AF', fontSize: 11 }} itemStyle={{ color: '#00ccb4', fontSize: 12 }} />
                                <Legend wrapperStyle={{ fontSize: 11, color: '#9CA3AF' }} />
                                <Line type="monotone" dataKey="impressions" stroke="#00ccb4" strokeWidth={2} dot={{ fill: '#00ccb4', r: 4 }} activeDot={{ r: 6, stroke: '#00ffda', strokeWidth: 2 }} />
                                <Line type="monotone" dataKey="reach" stroke="#06b6d4" strokeWidth={2} dot={{ fill: '#06b6d4', r: 3 }} />
                            </LineChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="h-[280px] flex items-center justify-center text-gray-600 text-xs font-bold tracking-widest uppercase">
                            No data available yet
                        </div>
                    )}
                </div>

                {/* Bar Chart — Reach per post */}
                <div className="glass-card p-6">
                    <h3 className="text-xs font-bold uppercase tracking-[0.3em] text-gray-500 mb-6">Reach Per Post</h3>
                    {barData.length > 0 ? (
                        <ResponsiveContainer width="100%" height={280}>
                            <BarChart data={barData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(20,50,50,0.4)" />
                                <XAxis dataKey="name" tick={{ fontSize: 9, fill: '#6B7280' }} angle={-20} textAnchor="end" height={60} />
                                <YAxis tick={{ fontSize: 10, fill: '#6B7280' }} />
                                <Tooltip contentStyle={customTooltipStyle} labelStyle={{ color: '#9CA3AF', fontSize: 11 }} itemStyle={{ fontSize: 12 }} />
                                <Bar dataKey="reach" fill="#00ccb4" radius={[6, 6, 0, 0]} />
                                <Bar dataKey="impressions" fill="#06b6d4" radius={[6, 6, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="h-[280px] flex items-center justify-center text-gray-600 text-xs font-bold tracking-widest uppercase">
                            No data available yet
                        </div>
                    )}
                </div>
            </div>

            {/* Best Performing Post */}
            {bestPost && bestPost.post && (
                <div className="glass-card p-6 border-brand/10 mb-8">
                    <div className="flex items-center gap-3 mb-5">
                        <Award size={20} className="text-brand" />
                        <h3 className="text-xs font-bold uppercase tracking-[0.3em] text-gray-500">Best Performing Post</h3>
                    </div>
                    <div className="flex gap-6 items-start">
                        {bestPost.post.image_url && (
                            <img
                                src={bestPost.post.image_url}
                                alt="Best post"
                                className="w-24 h-24 rounded-xl object-cover border border-pixora-border"
                            />
                        )}
                        <div className="flex-1">
                            <p className="text-white text-sm leading-relaxed mb-3">
                                {bestPost.post.caption?.substring(0, 120)}{bestPost.post.caption && bestPost.post.caption.length > 120 ? '...' : ''}
                            </p>
                            <div className="flex gap-6">
                                <div>
                                    <span className="text-[10px] font-bold uppercase tracking-widest text-gray-500 block">Engagement Rate</span>
                                    <span className="text-brand font-black text-lg">{bestPost.engagement_rate.toFixed(1)}%</span>
                                </div>
                                <div>
                                    <span className="text-[10px] font-bold uppercase tracking-widest text-gray-500 block">Reach</span>
                                    <span className="text-white font-bold text-lg">{bestPost.reach.toLocaleString()}</span>
                                </div>
                                <div>
                                    <span className="text-[10px] font-bold uppercase tracking-widest text-gray-500 block">Platform</span>
                                    <span className="text-white font-bold text-lg capitalize">{bestPost.post.platform}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Empty State */}
            {!isLoading && postAnalytics.length === 0 && !platformInsights && (
                <div className="glass-card p-12 text-center border-dashed">
                    <BarChart3 size={48} className="text-gray-700 mx-auto mb-4" />
                    <h3 className="text-white font-bold text-lg mb-2">No Analytics Data Yet</h3>
                    <p className="text-gray-500 text-sm max-w-md mx-auto">
                        Analytics will populate as posts are published and tracked.
                        Click <strong className="text-brand">REFRESH</strong> to fetch live data from Facebook and Instagram.
                    </p>
                </div>
            )}
        </div>
    );
};

export default DashboardPage;
