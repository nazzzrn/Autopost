import React, { useState } from 'react';
import { useWorkflowStore } from '../store';
import { Send, Loader2, PenTool } from 'lucide-react';

const PromptStep: React.FC = () => {
    const [prompt, setPrompt] = useState("");
    const { startWorkflow, isLoading, error } = useWorkflowStore();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!prompt.trim()) return;
        await startWorkflow(prompt);
    };

    return (
        <div className="max-w-3xl mx-auto mt-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="glass-card p-8 relative overflow-hidden group">
                <div className="absolute top-0 right-0 -translate-y-1/2 translate-x-1/2 w-64 h-64 bg-brand/5 blur-3xl rounded-full transition-transform duration-700 group-hover:scale-125 pointer-events-none" />

                <div className="relative z-10">
                    <div className="flex items-center gap-4 mb-8">
                        <div className="w-12 h-12 rounded-xl bg-brand/10 border border-brand/20 flex items-center justify-center text-brand">
                            <PenTool size={24} />
                        </div>
                        <div>
                            <h2 className="text-3xl font-bold text-white tracking-tight">Create New Workflow</h2>
                            <p className="text-gray-400 text-sm mt-1 font-medium">Harness AI to automate your content strategy</p>
                        </div>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-8">
                        <div className="space-y-3">
                            <label className="text-xs font-bold uppercase tracking-[0.2em] text-gray-500 ml-1">
                                Goal Description
                            </label>
                            <textarea
                                className="pixora-input w-full min-h-[180px] resize-none text-lg leading-relaxed pt-5"
                                placeholder="e.g. Create and publish a post about space exploration on Instagram and Twitter... "
                                value={prompt}
                                onChange={(e) => setPrompt(e.target.value)}
                                disabled={isLoading}
                            />
                        </div>

                        {error && (
                            <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl text-sm flex items-center gap-3 animate-in fade-in zoom-in duration-300">
                                <div className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
                                {error}
                            </div>
                        )}

                        <div className="flex items-center justify-between pt-4 border-t border-pixora-border/50">
                            <div className="flex items-center gap-2 text-gray-500 text-xs font-semibold tracking-wider">
                                <div className="w-1.5 h-1.5 rounded-full bg-brand" />
                                AI-POWERED AUTOMATION ENABLED
                            </div>
                            <button
                                type="submit"
                                disabled={isLoading || !prompt.trim()}
                                className="pixora-btn-primary flex items-center gap-3 disabled:opacity-30 disabled:hover:scale-100"
                            >
                                {isLoading ? (
                                    <>
                                        <Loader2 className="animate-spin" size={20} />
                                        <span>INITIALIZING...</span>
                                    </>
                                ) : (
                                    <>
                                        <Send size={18} />
                                        <span>LAUNCH WORKFLOW</span>
                                    </>
                                )}
                            </button>
                        </div>
                    </form>
                </div>
            </div>

            <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
                {[
                    { title: "Smart Scheduling", desc: "Optimal posting times" },
                    { title: "Visual AI", desc: "Flux-1 Generation" },
                    { title: "Cross-platform", desc: "One-click publishing" }
                ].map((item, i) => (
                    <div key={i} className="glass-card p-4 border-brand/5 bg-brand/[0.02] hover:bg-brand/[0.05] transition-colors cursor-default">
                        <h4 className="text-white text-[10px] font-bold tracking-widest uppercase mb-1">{item.title}</h4>
                        <p className="text-gray-500 text-[10px] font-medium">{item.desc}</p>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default PromptStep;
