import React, { useState } from 'react';
import { useWorkflowStore } from '../store';
import { Check, RefreshCw, MessageSquare } from 'lucide-react';

const CaptionReview: React.FC = () => {
    const { platforms, captions, caption_options, reviewCaption, isLoading, error, regenerate_count_caption, generateCaption, generatingPlatforms } = useWorkflowStore();
    const [localCaptions, setLocalCaptions] = React.useState(captions);
    const [feedback, setFeedback] = useState("");
    const [showReject, setShowReject] = useState(false);

    // Sync local state when global captions are updated
    React.useEffect(() => {
        setLocalCaptions(captions);
    }, [captions]);

    const handleAccept = async () => {
        await reviewCaption(true, undefined, localCaptions);
    };

    const handleReject = async () => {
        if (!feedback.trim()) return;
        await reviewCaption(false, feedback);
        setShowReject(false);
    };

    const handleCaptionChange = (platform: string, text: string) => {
        setLocalCaptions(prev => ({ ...prev, [platform]: text }));
    };

    if (showReject) {
        return (
            <div className="max-w-2xl mx-auto mt-10">
                <div className="glass-card p-8 border-red-500/20 relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-red-500/0 via-red-500/50 to-red-500/0" />
                    <h3 className="text-2xl font-bold mb-2 text-white">Refine AI Output</h3>
                    <p className="text-sm text-gray-500 mb-6 font-medium uppercase tracking-wider">Attempt {regenerate_count_caption} of 3</p>

                    <textarea
                        className="pixora-input w-full min-h-[120px] mb-6 border-red-500/10 focus:border-red-500/30"
                        placeholder="What should be changed? (e.g. more professional, shorter, more emojis...)"
                        value={feedback}
                        onChange={e => setFeedback(e.target.value)}
                    />

                    <div className="flex justify-end gap-4">
                        <button onClick={() => setShowReject(false)} className="pixora-btn-secondary border-gray-700 text-gray-400 hover:text-white hover:bg-white/5">
                            CANCEL
                        </button>
                        <button
                            onClick={handleReject}
                            disabled={isLoading || !feedback.trim()}
                            className="px-8 py-2.5 bg-red-600/90 text-white font-bold rounded-full hover:bg-red-500 shadow-[0_0_20px_rgba(220,38,38,0.2)] transition-all disabled:opacity-30"
                        >
                            {isLoading ? "REGENERATING..." : "REGENERATE"}
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h2 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-brand/10 border border-brand/20 flex items-center justify-center text-brand">
                            <MessageSquare size={20} />
                        </div>
                        Review Captions
                    </h2>
                    <p className="text-gray-500 text-sm mt-1 ml-13">Tailor the AI-generated copy for each platform</p>
                </div>

                <button
                    onClick={() => useWorkflowStore.getState().generateAllCaptions()}
                    disabled={isLoading}
                    className="pixora-btn-primary flex items-center gap-2"
                >
                    <RefreshCw className={isLoading ? "animate-spin" : ""} size={18} />
                    GENERATE ALL
                </button>
            </div>

            <div className="grid gap-8">
                {platforms.map((platform) => {
                    const text = localCaptions[platform] || "";
                    const isGenerating = generatingPlatforms[platform];

                    return (
                        <div key={platform} className="glass-card p-6 border-brand/5 relative group hover:border-brand/20 transition-all duration-500">
                            <div className="flex items-center gap-2 mb-6">
                                <span className="w-2 h-2 rounded-full bg-brand shadow-[0_0_8px_rgba(0,204,180,1)]" />
                                <label className="text-xs font-black text-gray-400 uppercase tracking-[0.3em]">{platform}</label>
                            </div>

                            {caption_options[platform] && caption_options[platform].length > 0 ? (
                                <div className="space-y-6">
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                        {caption_options[platform].map((opt, idx) => (
                                            <div
                                                key={idx}
                                                className={`p-4 rounded-xl border transition-all cursor-pointer text-xs leading-relaxed font-medium ${text === opt
                                                    ? 'bg-brand/10 border-brand/30 text-brand shadow-[0_0_15px_rgba(0,204,180,0.1)]'
                                                    : 'bg-pixora-darker-green/30 border-pixora-border/50 text-gray-500 hover:border-brand/20'
                                                    }`}
                                                onClick={() => handleCaptionChange(platform, opt)}
                                            >
                                                <div className="flex items-start gap-3">
                                                    <div className={`mt-0.5 w-3 h-3 rounded-full border-2 flex-shrink-0 flex items-center justify-center ${text === opt ? 'border-brand bg-brand' : 'border-gray-700'
                                                        }`}>
                                                        {text === opt && <div className="w-1 h-1 bg-pixora-bg rounded-full" />}
                                                    </div>
                                                    <p className="font-mono tracking-tight">{opt}</p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>

                                    <div className="relative">
                                        <textarea
                                            className="pixora-input w-full min-h-[120px] pt-4 font-mono text-sm border-brand/10"
                                            value={text}
                                            onChange={(e) => handleCaptionChange(platform, e.target.value)}
                                            placeholder="Refine selected option or write from scratch..."
                                        />
                                        <div className="absolute top-0 right-4 -translate-y-1/2 bg-pixora-bg px-2 text-[10px] font-bold text-gray-600 tracking-widest uppercase">
                                            Editor
                                        </div>
                                    </div>
                                </div>
                            ) : (
                                <div className="flex flex-col items-center justify-center py-12 px-6 border-2 border-dashed border-pixora-border/50 rounded-2xl bg-pixora-darker-green/20">
                                    <RefreshCw className={`text-gray-700 mb-4 ${isGenerating ? 'animate-spin text-brand' : ''}`} size={32} />
                                    <p className="text-sm font-medium text-gray-500 mb-6">Awaiting content generation</p>
                                    <button
                                        onClick={() => generateCaption(platform, useWorkflowStore.getState().topic)}
                                        disabled={isGenerating}
                                        className="pixora-btn-secondary text-xs tracking-widest"
                                    >
                                        {isGenerating ? "PROCESSING..." : "GENERATE NOW"}
                                    </button>
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>

            {error && (
                <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl text-sm animate-pulse">
                    {error}
                </div>
            )}

            <div className="sticky bottom-8 z-20 flex justify-between items-center glass-card p-4 px-6 border-brand/20 shadow-[0_-10px_40px_rgba(0,0,0,0.5)]">
                <button
                    onClick={() => setShowReject(true)}
                    disabled={isLoading || regenerate_count_caption >= 3}
                    className="flex items-center gap-2 text-red-400 text-xs font-black tracking-widest hover:text-red-300 transition-colors disabled:opacity-30"
                >
                    <RefreshCw size={16} />
                    {regenerate_count_caption >= 3 ? "RETRIES MAXED" : "REJECT & RETRY"}
                </button>

                <button
                    onClick={handleAccept}
                    disabled={isLoading}
                    className="pixora-btn-primary flex items-center gap-3 px-10"
                >
                    <Check size={18} />
                    <span>APPROVE ALL</span>
                </button>
            </div>
        </div>
    );
};

export default CaptionReview;
