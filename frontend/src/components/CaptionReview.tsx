import React, { useState } from 'react';
import { useWorkflowStore } from '../store';
import { Check, RefreshCw, MessageSquare } from 'lucide-react';

const CaptionReview: React.FC = () => {
    const { captions, reviewCaption, isLoading, error, regenerate_count_caption } = useWorkflowStore();
    const [localCaptions, setLocalCaptions] = useState(captions);
    const [feedback, setFeedback] = useState("");
    const [showReject, setShowReject] = useState(false);

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
            <div className="max-w-2xl mx-auto p-6 bg-white dark:bg-gray-800 rounded-lg shadow-xl border-l-4 border-red-500 transition-colors">
                <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Provide Feedback to Regenerate</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">Attempts used: {regenerate_count_caption}/3</p>
                <textarea
                    className="w-full p-3 border dark:border-gray-700 rounded mb-4 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-300"
                    placeholder="e.g. Make it more professional, shorter, use more emojis..."
                    value={feedback}
                    onChange={e => setFeedback(e.target.value)}
                />
                <div className="flex justify-end gap-2">
                    <button onClick={() => setShowReject(false)} className="px-4 py-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">Cancel</button>
                    <button
                        onClick={handleReject}
                        disabled={isLoading || !feedback.trim()}
                        className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
                    >
                        {isLoading ? "Regenerating..." : "Regenerate Captions"}
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto p-6 space-y-6">
            <h2 className="text-2xl font-bold text-gray-800 dark:text-white flex items-center gap-2">
                <MessageSquare /> Review Captions
            </h2>

            <div className="grid gap-6 md:grid-cols-1">
                {Object.entries(localCaptions).map(([platform, text]) => (
                    <div key={platform} className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border border-gray-200 dark:border-gray-700 transition-colors">
                        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">{platform}</label>
                        <textarea
                            className="w-full p-2 border dark:border-gray-600 rounded bg-gray-50 dark:bg-gray-700 focus:bg-white dark:focus:bg-gray-600 text-gray-900 dark:text-white transition-colors min-h-[100px]"
                            value={text}
                            onChange={(e) => handleCaptionChange(platform, e.target.value)}
                        />
                    </div>
                ))}
            </div>

            {error && <div className="p-3 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200 rounded">{error}</div>}

            <div className="flex justify-between items-center bg-gray-50 dark:bg-gray-800 p-4 rounded-lg sticky bottom-0 border-t dark:border-gray-700 shadow-lg">
                <button
                    onClick={() => setShowReject(true)}
                    disabled={isLoading || regenerate_count_caption >= 3}
                    className="flex items-center gap-2 px-5 py-2.5 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-800 bg-white dark:bg-gray-900 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg transition-colors disabled:opacity-50"
                >
                    <RefreshCw size={18} />
                    {regenerate_count_caption >= 3 ? "Max Retries Reached" : "Reject & Regenerate"}
                </button>

                <button
                    onClick={handleAccept}
                    disabled={isLoading}
                    className="flex items-center gap-2 px-8 py-2.5 bg-green-600 text-white rounded-lg hover:bg-green-700 shadow-md transition-all hover:scale-105"
                >
                    <Check size={18} />
                    Approve Captions
                </button>
            </div>
        </div>
    );
};

export default CaptionReview;
