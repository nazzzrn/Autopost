import React, { useEffect } from 'react';
import { Routes, Route, NavLink, useLocation } from 'react-router-dom';
import { useWorkflowStore } from './store';
import PromptStep from './components/PromptStep';
import CaptionReview from './components/CaptionReview';
import ImageReview from './components/ImageReview';
import ScheduleStep from './components/ScheduleStep';
import PublishStatus from './components/PublishStatus';
import CalendarPage from './pages/CalendarPage';
import DashboardPage from './pages/DashboardPage';
import { LayoutDashboard, PenTool, Image as ImageIcon, Calendar, Send, BarChart3, Zap } from 'lucide-react';

const StepIndicator = ({ currentStep }: { currentStep: string }) => {
    const steps = [
        { id: 'prompt', label: 'Prompt', icon: LayoutDashboard },
        { id: 'review_caption', label: 'Captions', icon: PenTool },
        { id: 'review_image', label: 'Image', icon: ImageIcon },
        { id: 'schedule', label: 'Schedule', icon: Calendar },
        { id: 'publish', label: 'Publish', icon: Send },
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
        <div className="flex justify-center items-center mb-16 gap-4 md:gap-8 overflow-x-auto pb-4 px-2">
            {steps.map((step, index) => {
                const status = getStepStatus(step.id);
                const Icon = step.icon;
                return (
                    <React.Fragment key={step.id}>
                        <div className="flex flex-col items-center group">
                            <div className={`relative w-14 h-14 rounded-2xl flex items-center justify-center transition-all duration-500 ${status === 'current'
                                ? 'bg-brand/20 border-2 border-brand text-brand shadow-[0_0_20px_rgba(0,204,180,0.4)]'
                                : status === 'completed'
                                    ? 'bg-brand text-pixora-bg'
                                    : 'bg-pixora-darker-green/50 border border-pixora-border text-gray-500'
                                }`}>
                                <Icon size={24} className={status === 'current' ? 'animate-pulse' : ''} />
                                {status === 'completed' && (
                                    <div className="absolute -top-1 -right-1 bg-white text-pixora-bg rounded-full p-0.5">
                                        <div className="w-3 h-3 bg-brand rounded-full" />
                                    </div>
                                )}
                            </div>
                            <span className={`text-xs mt-3 font-medium tracking-wider uppercase transition-colors duration-300 ${status === 'current' ? 'text-brand' : status === 'completed' ? 'text-brand/80' : 'text-gray-600'
                                }`}>
                                {step.label}
                            </span>
                        </div>
                        {index < steps.length - 1 && (
                            <div className={`h-[2px] w-8 md:w-12 rounded-full mb-6 ${getStepStatus(steps[index + 1].id) !== 'upcoming' ? 'bg-brand/50' : 'bg-pixora-border'
                                }`} />
                        )}
                    </React.Fragment>
                );
            })}
        </div>
    );
};

// Workflow page — preserves the existing step-by-step flow exactly
const WorkflowPage: React.FC = () => {
    const { current_step, fetchState } = useWorkflowStore();

    useEffect(() => {
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
        <>
            <StepIndicator currentStep={current_step} />
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-700">
                {renderStep()}
            </div>
        </>
    );
};

const navItems = [
    { to: '/', label: 'Workflow', icon: Zap },
    { to: '/calendar', label: 'Calendar', icon: Calendar },
    { to: '/dashboard', label: 'Dashboard', icon: BarChart3 },
];

function App() {
    const location = useLocation();

    useEffect(() => {
        document.documentElement.classList.add('dark');
    }, []);

    return (
        <div className="min-h-screen bg-pixora-bg flex flex-col selection:bg-brand/30 selection:text-brand">
            {/* Background Glows */}
            <div className="fixed top-0 right-0 w-[500px] h-[500px] bg-brand/10 blur-[120px] rounded-full -translate-y-1/2 translate-x-1/2 pointer-events-none" />
            <div className="fixed bottom-0 left-0 w-[400px] h-[400px] bg-accent-cyan/5 blur-[100px] rounded-full translate-y-1/2 -translate-x-1/2 pointer-events-none" />

            <header className="relative z-10 border-b border-pixora-border bg-pixora-bg/50 backdrop-blur-md">
                <div className="max-w-7xl mx-auto px-6 py-5 flex justify-between items-center">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-brand rounded-xl flex items-center justify-center shadow-[0_0_20px_rgba(0,204,180,0.4)]">
                            <span className="text-pixora-bg font-black text-xl">P</span>
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                                Pixora <span className="text-brand text-sm font-normal px-2 py-0.5 rounded-full bg-brand/10 border border-brand/20">v2.0</span>
                            </h1>
                            <p className="text-[10px] text-gray-500 uppercase tracking-[0.2em] font-medium">Content Automation Suite</p>
                        </div>
                    </div>

                    {/* Navigation */}
                    <nav className="flex items-center gap-1 bg-pixora-darker-green/50 border border-pixora-border rounded-2xl p-1.5">
                        {navItems.map(item => {
                            const Icon = item.icon;
                            const isActive = location.pathname === item.to;
                            return (
                                <NavLink
                                    key={item.to}
                                    to={item.to}
                                    className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-widest transition-all duration-300 ${isActive
                                        ? 'bg-brand/15 text-brand border border-brand/20 shadow-[0_0_10px_rgba(0,204,180,0.15)]'
                                        : 'text-gray-500 hover:text-gray-300 border border-transparent'
                                        }`}
                                >
                                    <Icon size={14} />
                                    <span className="hidden md:inline">{item.label}</span>
                                </NavLink>
                            );
                        })}
                    </nav>
                </div>
            </header>

            <main className="relative z-10 flex-1 max-w-6xl mx-auto w-full p-6 md:p-12 overflow-hidden">
                <Routes>
                    <Route path="/" element={<WorkflowPage />} />
                    <Route path="/calendar" element={<CalendarPage />} />
                    <Route path="/dashboard" element={<DashboardPage />} />
                </Routes>
            </main>
        </div>
    );
}

export default App;
