import React, { useState } from 'react';
import { useWorkflowStore } from '../store';
import { Check, RefreshCw, Upload, Image as ImageIcon } from 'lucide-react';

const ImageReview: React.FC = () => {
    const { image_path, reviewImage, isLoading, error, regenerate_count_image } = useWorkflowStore();
    const [feedback, setFeedback] = useState("");
    const [showReject, setShowReject] = useState(false);
    const [uploadedImage, setUploadedImage] = useState<string | null>(null);

    // Determines which image to show/use
    const currentImage = uploadedImage || image_path;

    const handleAccept = async () => {
        // If uploaded, we pass that as the "image_path"
        await reviewImage(true, undefined, uploadedImage || undefined);
    };

    const handleReject = async () => {
        if (!feedback.trim()) return;
        await reviewImage(false, feedback);
        setShowReject(false);
        setUploadedImage(null); // Reset upload on regenerate
    };

    const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            // Create a fake local URL for preview
            const url = URL.createObjectURL(file);
            setUploadedImage(url);
            // In a real app, we'd upload to server here.
            // For now, we use the blob URL or simulated path.
            // Ideally we should base64 it to send to backend or just keep the path if local agent.
            // Let's assume the user manually puts the path if they select "Upload" 
            // OR we just use the blob URL for display and assume backend handles logic.
            // For the requirements "single user system", "local workspace",
            // We can try to get the file path but browsers block it.
            // We will stick to the blob URL for UI and maybe send a "dummy_upload.jpg" string to backend.
        }
    };

    if (showReject) {
        return (
            <div className="max-w-2xl mx-auto p-6 bg-white dark:bg-gray-800 rounded-lg shadow-xl border-l-4 border-red-500 transition-colors">
                <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Provide Feedback to Regenerate Image</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">Attempts used: {regenerate_count_image}/3</p>
                <textarea
                    className="w-full p-3 border dark:border-gray-700 rounded mb-4 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-300"
                    placeholder="e.g. Make it brighter, add mountains..."
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
                        {isLoading ? "Regenerating..." : "Regenerate Image"}
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto p-6 space-y-6">
            <h2 className="text-2xl font-bold text-gray-800 dark:text-white flex items-center gap-2">
                <ImageIcon /> Review Image
            </h2>

            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow border border-gray-200 dark:border-gray-700 transition-colors">
                <div className="aspect-video bg-gray-100 dark:bg-gray-900 rounded-lg flex items-center justify-center overflow-hidden mb-4 border border-dashed border-gray-300 dark:border-gray-600 relative group">
                    {currentImage ? (
                        <img src={currentImage} alt="Generated Content" className="w-full h-full object-contain" />
                    ) : (
                        <div className="text-gray-400 dark:text-gray-500 flex flex-col items-center">
                            <ImageIcon size={48} />
                            <span>No image generated</span>
                        </div>
                    )}

                    {/* Overlay for upload */}
                    <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                        <label className="cursor-pointer bg-white text-gray-800 px-4 py-2 rounded-full font-bold hover:scale-105 transition-transform flex items-center gap-2 shadow-lg">
                            <Upload size={18} />
                            Change Image
                            <input type="file" className="hidden" accept="image/*" onChange={handleFileUpload} />
                        </label>
                    </div>
                </div>

                <p className="text-sm text-gray-500 dark:text-gray-400 text-center">
                    {uploadedImage ? "Using uploaded image" : "Generated by Gemini"}
                </p>
            </div>

            {error && <div className="p-3 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200 rounded">{error}</div>}

            <div className="flex justify-between items-center bg-gray-50 dark:bg-gray-800 p-4 rounded-lg sticky bottom-0 border-t dark:border-gray-700 shadow-lg">
                <button
                    onClick={() => setShowReject(true)}
                    disabled={isLoading || regenerate_count_image >= 3}
                    className="flex items-center gap-2 px-5 py-2.5 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-800 bg-white dark:bg-gray-900 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg transition-colors disabled:opacity-50"
                >
                    <RefreshCw size={18} />
                    {regenerate_count_image >= 3 ? "Max Retries Reached" : "Reject & Regenerate"}
                </button>

                <button
                    onClick={handleAccept}
                    disabled={isLoading || !currentImage}
                    className="flex items-center gap-2 px-8 py-2.5 bg-green-600 text-white rounded-lg hover:bg-green-700 shadow-md transition-all hover:scale-105 disabled:opacity-50 disabled:scale-100"
                >
                    <Check size={18} />
                    Approve Image
                </button>
            </div>
        </div>
    );
};

export default ImageReview;
