import React, { useEffect, useState } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from '@fullcalendar/interaction';
import { useCalendarStore, CalendarPost } from '../stores/calendarStore';
import { Calendar, X, Instagram, Facebook, Clock, CheckCircle, AlertTriangle, FileText } from 'lucide-react';

const statusColors: Record<string, { bg: string; border: string; text: string }> = {
    draft: { bg: '#374151', border: '#4B5563', text: '#9CA3AF' },
    scheduled: { bg: '#1E3A5F', border: '#2563EB', text: '#60A5FA' },
    published: { bg: '#064E3B', border: '#059669', text: '#34D399' },
    failed: { bg: '#7F1D1D', border: '#DC2626', text: '#F87171' },
};

const statusIcons: Record<string, React.ReactNode> = {
    draft: <FileText size={14} />,
    scheduled: <Clock size={14} />,
    published: <CheckCircle size={14} />,
    failed: <AlertTriangle size={14} />,
};

const CalendarPage: React.FC = () => {
    const { posts, isLoading, error, fetchPosts } = useCalendarStore();
    const [selectedPost, setSelectedPost] = useState<CalendarPost | null>(null);

    useEffect(() => {
        fetchPosts();
    }, []);

    // Map posts to FullCalendar events
    const events = posts
        .filter(p => p.scheduled_time || p.published_time)
        .map(p => {
            const colors = statusColors[p.status] || statusColors.draft;
            const platformEmoji = p.platform === 'instagram' ? '📸' : '📘';
            return {
                id: p.id,
                title: `${platformEmoji} ${p.caption.substring(0, 35)}${p.caption.length > 35 ? '...' : ''}`,
                start: p.scheduled_time || p.published_time || p.created_at,
                backgroundColor: colors.bg,
                borderColor: colors.border,
                textColor: colors.text,
                extendedProps: { post: p },
            };
        });

    const handleEventClick = (info: any) => {
        const post = info.event.extendedProps.post as CalendarPost;
        setSelectedPost(post);
    };

    const formatDate = (isoDate: string | null) => {
        if (!isoDate) return '—';
        try {
            return new Date(isoDate).toLocaleString('en-US', {
                month: 'short', day: 'numeric', year: 'numeric',
                hour: '2-digit', minute: '2-digit'
            });
        } catch { return isoDate; }
    };

    return (
        <div className="min-h-screen bg-pixora-bg">
            {/* Header */}
            <div className="mb-8 flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-brand/10 border border-brand/20 flex items-center justify-center text-brand">
                        <Calendar size={24} />
                    </div>
                    <div>
                        <h2 className="text-3xl font-bold text-white tracking-tight">Content Calendar</h2>
                        <p className="text-gray-500 text-sm mt-1 font-medium">View your scheduled and published posts</p>
                    </div>
                </div>

                {/* Post counts */}
                <div className="flex gap-4">
                    {Object.entries(statusColors).map(([status, colors]) => {
                        const count = posts.filter(p => p.status === status).length;
                        if (count === 0) return null;
                        return (
                            <div key={status} className="flex items-center gap-2 px-3 py-1.5 rounded-xl border bg-pixora-darker-green/30" style={{ borderColor: colors.border + '40' }}>
                                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: colors.border }} />
                                <span className="text-[10px] font-bold uppercase tracking-widest" style={{ color: colors.text }}>{count} {status}</span>
                            </div>
                        );
                    })}
                </div>
            </div>

            {error && (
                <div className="mb-4 p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl text-sm">
                    {error}
                </div>
            )}

            {/* Calendar */}
            <div className="glass-card p-6 calendar-wrapper">
                <FullCalendar
                    plugins={[dayGridPlugin, interactionPlugin]}
                    initialView="dayGridMonth"
                    events={events}
                    editable={false}
                    eventClick={handleEventClick}
                    headerToolbar={{
                        left: 'prev,next today',
                        center: 'title',
                        right: 'dayGridMonth',
                    }}
                    height="auto"
                    dayMaxEvents={3}
                />
            </div>

            {/* Empty state */}
            {!isLoading && posts.length === 0 && (
                <div className="mt-8 glass-card p-12 text-center border-dashed">
                    <Calendar size={48} className="text-gray-700 mx-auto mb-4" />
                    <h3 className="text-white font-bold text-lg mb-2">No Posts Yet</h3>
                    <p className="text-gray-500 text-sm max-w-md mx-auto">
                        Posts will appear here once you schedule or publish content through the <strong className="text-brand">Workflow</strong>.
                    </p>
                </div>
            )}

            {/* Detail Modal (read-only) */}
            {selectedPost && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={() => setSelectedPost(null)}>
                    <div className="glass-card p-8 w-full max-w-lg relative animate-in fade-in zoom-in duration-300" onClick={e => e.stopPropagation()}>
                        <button
                            onClick={() => setSelectedPost(null)}
                            className="absolute top-4 right-4 text-gray-500 hover:text-white transition-colors"
                        >
                            <X size={20} />
                        </button>

                        <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-3">
                            Post Details
                            <span
                                className="px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest"
                                style={{
                                    backgroundColor: (statusColors[selectedPost.status]?.bg || '#374151') + '80',
                                    color: statusColors[selectedPost.status]?.text || '#9CA3AF',
                                    border: `1px solid ${statusColors[selectedPost.status]?.border || '#4B5563'}40`,
                                }}
                            >
                                {statusIcons[selectedPost.status]} {selectedPost.status}
                            </span>
                        </h3>

                        {/* Image preview */}
                        {selectedPost.image_url && (
                            <div className="mb-5 rounded-xl overflow-hidden border border-pixora-border">
                                <img src={selectedPost.image_url} alt="Post" className="w-full h-40 object-cover" />
                            </div>
                        )}

                        <div className="space-y-4">
                            {/* Platform */}
                            <div className="flex items-center gap-3">
                                <div className="w-8 h-8 rounded-lg bg-pixora-darker-green/50 border border-pixora-border flex items-center justify-center">
                                    {selectedPost.platform === 'instagram' ? <Instagram size={16} className="text-pink-400" /> : <Facebook size={16} className="text-blue-400" />}
                                </div>
                                <span className="text-white font-semibold text-sm capitalize">{selectedPost.platform}</span>
                            </div>

                            {/* Caption */}
                            <div>
                                <label className="text-[10px] font-bold uppercase tracking-[0.3em] text-gray-600 block mb-1">Caption</label>
                                <p className="text-gray-300 text-sm leading-relaxed bg-pixora-darker-green/30 border border-pixora-border rounded-xl p-4">
                                    {selectedPost.caption || <span className="text-gray-600 italic">No caption</span>}
                                </p>
                            </div>

                            {/* Times */}
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="text-[10px] font-bold uppercase tracking-[0.3em] text-gray-600 block mb-1">Scheduled</label>
                                    <span className="text-gray-400 text-xs font-mono">{formatDate(selectedPost.scheduled_time)}</span>
                                </div>
                                <div>
                                    <label className="text-[10px] font-bold uppercase tracking-[0.3em] text-gray-600 block mb-1">Published</label>
                                    <span className="text-gray-400 text-xs font-mono">{formatDate(selectedPost.published_time)}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default CalendarPage;
