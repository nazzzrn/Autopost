import React, { useEffect } from 'react';
import { useWorkflowStore } from '../store';
import { CheckCircle, Loader2, Send, AlertTriangle } from 'lucide-react';

const PublishStatus: React.FC = () => {
    const { publish, publish_status, isLoading, error, current_step } = useWorkflowStore();
    const hasPublished = React.useRef(false);

    useEffect(() => {
        if (current_step === "publish" && !hasPublished.current) {
            hasPublished.current = true;
            publish();
        }
    }, [current_step]);

    const platforms = ["Instagram", "Facebook", "LinkedIn"];

    return (
        <div className="max-w-2xl mx-auto p-6 bg-white dark:bg-gray-800 rounded-lg shadow-xl mt-10 transition-colors">
            <h2 className="text-2xl font-bold mb-6 text-gray-800 dark:text-white flex items-center gap-2">
                <Send /> Publishing Status
            </h2>

            <div className="space-y-4">
                {platforms.map((platform) => {
                    // Check if this platform was selected in the workflow
                    // We need to access the 'platforms' from store state
                    const isSelected = useWorkflowStore.getState().platforms.includes(platform);

                    if (!isSelected) {
                        return null; // Don't show unselected platforms
                    }

                    const status = publish_status[platform];
                    const isPublished = status && status.includes("Published"); // Simple check
                    const isFailed = status && status.includes("Failed");

                    return (
                        <div key={platform} className="flex items-center justify-between p-4 border dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-700 transition-colors">
                            <span className="font-semibold text-gray-700 dark:text-gray-200">{platform}</span>

                            {isPublished ? (
                                <div className="flex items-center gap-2 text-green-600 dark:text-green-400">
                                    <CheckCircle size={20} />
                                    <span>Success</span>
                                </div>
                            ) : isFailed ? (
                                <div className="flex items-center gap-2 text-red-600 dark:text-red-400">
                                    <AlertTriangle size={20} />
                                    <span>Failed</span>
                                </div>
                            ) : status ? (
                                <span className="text-gray-500 dark:text-gray-400">{status}</span>
                            ) : (
                                <div className="flex items-center gap-2 text-gray-400 dark:text-gray-500">
                                    {isLoading ? <Loader2 className="animate-spin" size={20} /> : <span>Pending...</span>}
                                </div>
                            )}
                        </div>
                    );
                })}
                {/* Fallback if no platforms selected? Should not happen if filtered correctly upstream */}
                {useWorkflowStore.getState().platforms.length === 0 && (
                    <div className="text-center text-gray-500 dark:text-gray-400 py-4">No platforms selected to publish.</div>
                )}
            </div>

            {current_step === "completed" && (
                <div className="mt-8 p-4 bg-green-50 dark:bg-green-900/30 text-green-800 dark:text-green-300 rounded-lg text-center font-bold border border-green-200 dark:border-green-800">
                    Workflow Completed Successfully!
                </div>
            )}

            {error && (
                <div className="mt-4 p-3 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-md text-sm border border-red-200 dark:border-red-800">
                    {error}
                </div>
            )}
        </div>
    );
};

export default PublishStatus;
