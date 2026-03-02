import React, { useState } from 'react';
import { useWorkflowStore } from '../store';
import { Check, RefreshCw, Upload, Image as ImageIcon, Loader2 } from 'lucide-react';

const ImageReview: React.FC = () => {
    const { image_path, topic, reviewImage, isLoading, error, regenerate_count_image, generateImage, isGeneratingImage } = useWorkflowStore();
    const [feedback, setFeedback] = useState("");
    const [showReject, setShowReject] = useState(false);
    const [uploadedImage, setUploadedImage] = useState<string | null>(null);

    // Determines which image to show/use
    const currentImage = uploadedImage || image_path;

    const handleAccept = async () => {
        await reviewImage(true, undefined, uploadedImage || undefined);
    };

    const handleReject = async () => {
        if (!feedback.trim()) return;
        await reviewImage(false, feedback);
        setShowReject(false);
        setUploadedImage(null);
    };

    const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
                const base64String = reader.result as string;
                setUploadedImage(base64String);
            };
            reader.readAsDataURL(file);
        }
    };

    if (showReject) {
        return (
            <div className="max-w-2xl mx-auto mt-10">
                <div className="glass-card p-8 border-red-500/20 relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-red-500/0 via-red-500/50 to-red-500/0" />
                    <h3 className="text-2xl font-bold mb-2 text-white">Regenerate Visual</h3>
                    <p className="text-sm text-gray-500 mb-6 font-medium uppercase tracking-wider">Attempt {regenerate_count_image} of 3</p>

                    <textarea
                        className="pixora-input w-full min-h-[120px] mb-6 border-red-500/10 focus:border-red-500/30"
                        placeholder="Describe the changes needed (e.g. more vibrant, cinematic lighting, different style...)"
                        value={feedback}
                        onChange={e => setFeedback(e.target.value)}
                    />

                    <div className="flex justify-end gap-4">
                        <button onClick={() => setShowReject(false)} className="pixora-btn-secondary border-gray-700 text-gray-400 hover:text-white">
                            CANCEL
                        </button>
                        <button
                            onClick={handleReject}
                            disabled={isLoading || !feedback.trim()}
                            className="px-8 py-2.5 bg-red-600/90 text-white font-bold rounded-full hover:bg-red-500 shadow-[0_0_20px_rgba(220,38,38,0.2)] transition-all disabled:opacity-30"
                        >
                            {isLoading ? "PROCESSING..." : "REGENERATE"}
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
                            <ImageIcon size={20} />
                        </div>
                        Visual Review
                    </h2>
                    <p className="text-gray-500 text-sm mt-1 ml-13">Finalize the creative asset for your workflow</p>
                </div>
            </div>

            <div className="glass-card p-4 relative group overflow-hidden">
                <div className="aspect-video bg-pixora-darker-green/50 rounded-xl flex items-center justify-center overflow-hidden border border-pixora-border/50 relative">
                    {currentImage ? (
                        <div className="relative w-full h-full group/img">
                            <img src={currentImage} alt="Generated Content" className="w-full h-full object-cover transition-transform duration-700 group-hover/img:scale-105" />
                            <div className="absolute inset-0 bg-gradient-to-t from-pixora-bg/80 via-transparent to-transparent opacity-0 group-hover/img:opacity-100 transition-opacity duration-300" />
                        </div>
                    ) : (
                        <div className="text-gray-600 flex flex-col items-center">
                            <div className="w-20 h-20 rounded-full bg-pixora-bg border border-pixora-border flex items-center justify-center mb-4">
                                <ImageIcon size={40} className="text-gray-700" />
                            </div>
                            <span className="text-sm font-bold tracking-widest uppercase">No Preview Available</span>
                        </div>
                    )}

                    {/* Overlay for upload */}
                    <div className="absolute inset-0 bg-pixora-bg/40 backdrop-blur-[2px] opacity-0 group-hover:opacity-100 transition-all duration-300 flex items-center justify-center">
                        <label className="cursor-pointer bg-brand text-pixora-bg px-6 py-3 rounded-full font-black text-xs tracking-widest hover:scale-105 active:scale-95 transition-all flex items-center gap-2 shadow-[0_0_20px_rgba(0,204,180,0.4)]">
                            <Upload size={16} />
                            REPLACE IMAGE
                            <input type="file" className="hidden" accept="image/*" onChange={handleFileUpload} />
                        </label>
                    </div>
                </div>

                <div className="absolute top-6 left-6 flex gap-2">
                    <span className={`px-3 py-1 rounded-full text-[10px] font-bold tracking-tighter uppercase ${uploadedImage ? 'bg-accent-cyan/20 text-accent-cyan border border-accent-cyan/30' : 'bg-brand/20 text-brand border border-brand/30'}`}>
                        {uploadedImage ? "User Upload" : "AI Generated"}
                    </span>
                    <span className="px-3 py-1 rounded-full bg-white/5 text-white/40 border border-white/10 text-[10px] font-bold tracking-tighter uppercase backdrop-blur-md">
                        Flux-1 Schnell
                    </span>
                </div>
            </div>

            {error && (
                <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl text-sm animate-pulse">
                    {error}
                </div>
            )}

            <div className="sticky bottom-8 z-20 flex justify-between items-center glass-card p-4 px-6 border-brand/20 shadow-[0_-10px_40px_rgba(0,0,0,0.5)]">
                <button
                    onClick={() => setShowReject(true)}
                    disabled={isLoading || regenerate_count_image >= 3}
                    className="flex items-center gap-2 text-red-400 text-xs font-black tracking-widest hover:text-red-300 transition-colors disabled:opacity-30"
                >
                    <RefreshCw size={16} />
                    {regenerate_count_image >= 3 ? "SYSTEM CAP REACHED" : "REJECT & RETRY"}
                </button>

                <div className="flex gap-4">
                    <button
                        onClick={() => generateImage(topic)}
                        disabled={isLoading || isGeneratingImage}
                        className="pixora-btn-secondary flex items-center gap-2 px-6"
                    >
                        {isGeneratingImage ? <Loader2 className="animate-spin" size={16} /> : <RefreshCw size={16} />}
                        <span className="text-xs">REGENERATE</span>
                    </button>

                    <button
                        onClick={handleAccept}
                        disabled={isLoading || isGeneratingImage || !currentImage}
                        className="pixora-btn-primary flex items-center gap-3 px-10 shadow-[0_0_30px_rgba(0,204,180,0.3)]"
                    >
                        <Check size={18} />
                        <span>APPROVE ASSET</span>
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ImageReview;
