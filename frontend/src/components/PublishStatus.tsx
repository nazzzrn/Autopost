import React, { useEffect } from 'react';
import { useWorkflowStore } from '../store';
import { CheckCircle, Loader2, Send, AlertTriangle, Clock } from 'lucide-react';

const PublishStatus: React.FC = () => {
    const { publish, publish_status, isLoading, error, current_step } = useWorkflowStore();
    const hasPublished = React.useRef(false);

    useEffect(() => {
        // Only auto-publish if we're in "publish" step AND no status yet
        // (If status already has "Scheduled", don't publish — it was a future schedule)
        const hasExistingStatus = Object.keys(publish_status).length > 0;
        if (current_step === "publish" && !hasPublished.current && !hasExistingStatus) {
            hasPublished.current = true;
            publish();
        }
    }, [current_step]);

    const platforms = ["Instagram", "Facebook", "LinkedIn"];

    return (
        <div className="max-w-3xl mx-auto mt-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="glass-card p-8 relative overflow-hidden group">
                <div className="absolute top-0 right-0 -translate-y-1/2 translate-x-1/2 w-64 h-64 bg-brand/5 blur-3xl rounded-full pointer-events-none" />

                <div className="relative z-10">
                    <div className="flex items-center gap-4 mb-10">
                        <div className="w-12 h-12 rounded-xl bg-brand/10 border border-brand/20 flex items-center justify-center text-brand">
                            <Send size={24} />
                        </div>
                        <div>
                            <h2 className="text-3xl font-bold text-white tracking-tight">Dispatch Registry</h2>
                            <p className="text-gray-500 text-sm mt-1 font-medium tracking-tight">Real-time monitoring of your content deployment</p>
                        </div>
                    </div>

                    <div className="space-y-4">
                        {platforms.map((platform) => {
                            const isSelected = useWorkflowStore.getState().platforms.includes(platform);
                            if (!isSelected) return null;

                            const status = publish_status[platform];
                            const isPublished = status && status.includes("Published");
                            const isFailed = status && status.includes("Failed");
                            const isScheduled = status && status.includes("Scheduled");

                            return (
                                <div key={platform} className={`flex items-center justify-between p-5 rounded-2xl border transition-all duration-500 ${isPublished
                                    ? 'bg-brand/5 border-brand/20'
                                    : isFailed
                                        ? 'bg-red-500/5 border-red-500/20'
                                        : isScheduled
                                            ? 'bg-blue-500/5 border-blue-500/20'
                                            : 'bg-pixora-darker-green/30 border-pixora-border/50'
                                    }`}>
                                    <div className="flex items-center gap-4">
                                        <div className={`w-2 h-2 rounded-full ${isPublished ? 'bg-brand animate-pulse shadow-[0_0_8px_rgba(0,204,180,1)]' : isFailed ? 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,1)]' : isScheduled ? 'bg-blue-400 animate-pulse shadow-[0_0_8px_rgba(96,165,250,1)]' : 'bg-gray-600'
                                            }`} />
                                        <span className={`font-black text-xs uppercase tracking-[0.2em] ${isPublished ? 'text-brand' : isFailed ? 'text-red-400' : isScheduled ? 'text-blue-400' : 'text-gray-400'}`}>
                                            {platform}
                                        </span>
                                    </div>

                                    <div className="flex items-center gap-3">
                                        {isPublished ? (
                                            <div className="flex items-center gap-2 text-brand font-bold text-[10px] tracking-widest">
                                                <CheckCircle size={16} />
                                                DEPLOYED
                                            </div>
                                        ) : isScheduled ? (
                                            <div className="flex items-center gap-2 text-blue-400 font-bold text-[10px] tracking-widest">
                                                <Clock size={16} />
                                                SCHEDULED
                                            </div>
                                        ) : isFailed ? (
                                            <div className="flex items-center gap-2 text-red-400 font-bold text-[10px] tracking-widest">
                                                <AlertTriangle size={16} />
                                                ERROR
                                            </div>
                                        ) : status ? (
                                            <span className="text-[10px] font-mono text-gray-500 uppercase tracking-widest">{status}</span>
                                        ) : (
                                            <div className="flex items-center gap-2 text-gray-600 font-bold text-[10px] tracking-widest">
                                                {isLoading ? (
                                                    <>
                                                        <Loader2 className="animate-spin" size={16} />
                                                        <span>SYNCING...</span>
                                                    </>
                                                ) : (
                                                    <span>STANDBY</span>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            );
                        })}

                        {useWorkflowStore.getState().platforms.length === 0 && (
                            <div className="text-center p-12 glass-card border-dashed">
                                <p className="text-gray-500 text-xs font-bold tracking-widest uppercase">No Active Channels Routed</p>
                            </div>
                        )}
                    </div>

                    {current_step === "completed" && (
                        <div className="mt-10 p-6 bg-brand text-pixora-bg rounded-2xl text-center font-black tracking-widest uppercase shadow-[0_0_30px_rgba(0,204,180,0.3)] animate-in zoom-in duration-500">
                            Workflow Executed Successfully
                        </div>
                    )}

                    {error && (
                        <div className="mt-6 p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl text-[10px] font-bold tracking-widest uppercase">
                            SYSTEM FAULT: {error}
                        </div>
                    )}
                </div>
            </div>

            {current_step === "completed" && (
                <div className="mt-8 flex justify-center">
                    <button
                        onClick={async () => {
                            try {
                                await fetch('http://localhost:8000/workflow/reset', { method: 'POST' });
                            } catch (e) { /* ignore */ }
                            window.location.href = '/';
                        }}
                        className="pixora-btn-secondary text-[10px] tracking-[0.3em] px-12"
                    >
                        INITIALIZE NEW SESSION
                    </button>
                </div>
            )}
        </div>
    );
};

export default PublishStatus;
