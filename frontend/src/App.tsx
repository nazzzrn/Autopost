import React, { useEffect, useState } from 'react';
import { useWorkflowStore } from './store';
import PromptStep from './components/PromptStep';
import CaptionReview from './components/CaptionReview';
import ImageReview from './components/ImageReview';
import ScheduleStep from './components/ScheduleStep';
import PublishStatus from './components/PublishStatus';
import { LayoutDashboard, PenTool, Image as ImageIcon, Calendar, Send, Sun, Moon } from 'lucide-react';

const StepIndicator = ({ currentStep }: { currentStep: string }) => {
    const steps = [
        { id: 'prompt', label: 'Prompt', icon: LayoutDashboard },
        { id: 'review_caption', label: 'Captions', icon: PenTool },
        { id: 'review_image', label: 'Image', icon: ImageIcon },
        { id: 'schedule', label: 'Schedule', icon: Calendar },
        { id: 'publish', label: 'Publish', icon: Send },
        { id: 'completed', label: 'Done', icon: Send },
    ];

    const getStepStatus = (stepId: string) => {
        const stepOrder = ['prompt', 'review_caption', 'review_image', 'schedule', 'publish', 'completed'];
        const currentIndex = stepOrder.indexOf(currentStep);
        const stepIndex = stepOrder.indexOf(stepId);

        if (stepIndex < currentIndex) return 'completed';
        if (stepIndex === currentIndex) return 'current';
        return 'upcoming';
    };

    return (
        <div className="flex justify-between items-center mb-10 overflow-x-auto pb-4">
            {steps.map((step) => {
                const status = getStepStatus(step.id);
                const Icon = step.icon;
                return (
                    <div key={step.id} className={`flex flex-col items-center min-w-[80px] ${status === 'current' ? 'text-blue-600 dark:text-blue-400 font-bold' : status === 'completed' ? 'text-green-600 dark:text-green-400' : 'text-gray-400 dark:text-gray-500'}`}>
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center mb-2 ${status === 'current' ? 'bg-blue-100 dark:bg-blue-900' : status === 'completed' ? 'bg-green-100 dark:bg-green-900' : 'bg-gray-100 dark:bg-gray-800'}`}>
                            <Icon size={20} />
                        </div>
                        <span className="text-sm">{step.label}</span>
                    </div>
                );
            })}
        </div>
    );
};

function App() {
    const { current_step, fetchState } = useWorkflowStore();
    const [theme, setTheme] = useState(() => {
        if (typeof window !== 'undefined') {
            const savedTheme = localStorage.getItem('theme');
            if (savedTheme) {
                return savedTheme;
            }
            if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
                return 'dark';
            }
        }
        return 'light';
    });

    useEffect(() => {
        const root = document.documentElement;
        if (theme === 'dark') {
            root.classList.add('dark');
        } else {
            root.classList.remove('dark');
        }
        localStorage.setItem('theme', theme);
    }, [theme]);

    const toggleTheme = () => {
        setTheme(prev => prev === 'light' ? 'dark' : 'light');
    };

    useEffect(() => {
        // Initial fetch to sync state on reload
        fetchState();
    }, []);

    const renderStep = () => {
        switch (current_step) {
            case 'prompt':
                return <PromptStep />;
            case 'review_caption':
                return <CaptionReview />;
            case 'review_image':
                return <ImageReview />;
            case 'schedule':
                return <ScheduleStep />;
            case 'publish':
            case 'completed':
                return <PublishStatus />;
            default:
                return <PromptStep />;
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col transition-colors duration-200">
            <header className="bg-white dark:bg-gray-800 shadow-sm transition-colors duration-200">
                <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
                    <h1 className="text-xl font-bold flex items-center gap-2 text-gray-800 dark:text-white">
                        <span className="bg-blue-600 text-white p-1 rounded">CW</span> Content Workflow Agent
                    </h1>
                    <button
                        onClick={toggleTheme}
                        className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-gray-600 dark:text-gray-300"
                        aria-label="Toggle theme"
                    >
                        {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
                    </button>
                </div>
            </header>

            <main className="flex-1 max-w-5xl mx-auto w-full p-6 text-gray-900 dark:text-gray-100">
                <StepIndicator currentStep={current_step} />
                {renderStep()}
            </main>
        </div>
    );
}

export default App;
