import React, { useState } from 'react';
import { useWorkflowStore } from '../store';
import { Send, Loader2 } from 'lucide-react';

const PromptStep: React.FC = () => {
    const [prompt, setPrompt] = useState("");
    const { startWorkflow, isLoading, error } = useWorkflowStore();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!prompt.trim()) return;
        await startWorkflow(prompt);
    };

    return (
        <div className="max-w-2xl mx-auto p-6 bg-white dark:bg-gray-800 rounded-lg shadow-xl mt-10 transition-colors">
            <h2 className="text-2xl font-bold mb-4 text-gray-800 dark:text-white">New Content Workflow</h2>
            <p className="mb-4 text-gray-600 dark:text-gray-300">Describe what you want to post. Include topic, platforms, and optional time.</p>

            <form onSubmit={handleSubmit} className="space-y-4">
                <textarea
                    className="w-full p-4 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent min-h-[150px] bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-300 transition-colors"
                    placeholder="e.g. Create and publish a post about monkeys on Instagram and Facebook at 5pm tomorrow"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    disabled={isLoading}
                />

                {error && (
                    <div className="p-3 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200 rounded-md text-sm">
                        {error}
                    </div>
                )}

                <div className="flex justify-end">
                    <button
                        type="submit"
                        disabled={isLoading || !prompt.trim()}
                        className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg disabled:opacity-50 transition-colors"
                    >
                        {isLoading ? <Loader2 className="animate-spin" /> : <Send size={20} />}
                        Start Workflow
                    </button>
                </div>
            </form>
        </div>
    );
};

export default PromptStep;
