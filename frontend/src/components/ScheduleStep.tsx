import React, { useState } from 'react';
import { useWorkflowStore } from '../store';
import { Calendar, ArrowRight, Loader2 } from 'lucide-react';

const ScheduleStep: React.FC = () => {
    const { schedule, isLoading, error, schedule_time } = useWorkflowStore();
    const [date, setDate] = useState(schedule_time || "");

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!date) return;
        await schedule(date);
    };

    return (
        <div className="max-w-3xl mx-auto mt-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="glass-card p-10 relative overflow-hidden group">
                <div className="absolute top-0 right-0 -translate-y-1/2 translate-x-1/2 w-64 h-64 bg-accent-cyan/5 blur-3xl rounded-full pointer-events-none" />

                <div className="relative z-10">
                    <div className="flex items-center gap-4 mb-10">
                        <div className="w-12 h-12 rounded-xl bg-brand/10 border border-brand/20 flex items-center justify-center text-brand">
                            <Calendar size={24} />
                        </div>
                        <div>
                            <h2 className="text-3xl font-bold text-white tracking-tight">Schedule Launch</h2>
                            <p className="text-gray-500 text-sm mt-1 font-medium">Select the optimal time for your audience</p>
                        </div>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-10">
                        <div className="space-y-4">
                            <label className="text-xs font-bold uppercase tracking-[0.3em] text-gray-500 ml-1">
                                Target Publication Date & Time
                            </label>
                            <input
                                type="datetime-local"
                                className="pixora-input w-full text-lg font-mono py-5 border-brand/5 focus:border-brand/30"
                                value={date}
                                onChange={(e) => setDate(e.target.value)}
                                required
                            />
                        </div>

                        {error && (
                            <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl text-sm animate-pulse">
                                {error}
                            </div>
                        )}

                        <div className="flex items-center justify-between pt-8 border-t border-pixora-border/50">
                            <div className="flex items-center gap-2 text-gray-600 text-[10px] font-bold tracking-widest leading-none">
                                <div className="w-1.5 h-1.5 rounded-full bg-brand animate-pulse" />
                                AUTOMATED DISPATCH READY
                            </div>
                            <button
                                type="submit"
                                disabled={isLoading || !date}
                                className="pixora-btn-primary flex items-center gap-3 px-10"
                            >
                                {isLoading ? (
                                    <>
                                        <Loader2 className="animate-spin" size={20} />
                                        <span>SCHEDULING...</span>
                                    </>
                                ) : (
                                    <>
                                        <span>SCHEDULE & CONTINUE</span>
                                        <ArrowRight size={18} />
                                    </>
                                )}
                            </button>
                        </div>
                    </form>
                </div>
            </div>

            <div className="mt-8 glass-card p-6 border-brand/5 bg-brand/[0.02]">
                <div className="flex items-start gap-4">
                    <div className="w-8 h-8 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center text-white/40">
                        <ArrowRight size={16} />
                    </div>
                    <div>
                        <h4 className="text-white text-xs font-bold tracking-wider uppercase mb-1">Queue Protection</h4>
                        <p className="text-gray-500 text-[10px] font-medium leading-relaxed">Your content is encrypted and queued. Our agents will monitor the status and notify you once the publication is live.</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ScheduleStep;
