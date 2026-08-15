import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";
import heroImage from "@/assets/hero-research.jpg";
const Hero = () => {
    return <section className="relative min-h-[90vh] flex items-center justify-center overflow-hidden bg-gradient-to-br from-background via-background to-secondary">
        {/* Animated background elements */}
        <div className="absolute inset-0 overflow-hidden">
            <div className="absolute -top-1/2 -right-1/2 w-full h-full bg-primary/5 rounded-full blur-3xl animate-pulse-soft" />
            <div className="absolute -bottom-1/2 -left-1/2 w-full h-full bg-accent/5 rounded-full blur-3xl animate-pulse-soft" style={{
                animationDelay: '1s'
            }} />
        </div>

        <div className="container mx-auto px-4 relative z-10">
            <div className="grid lg:grid-cols-2 gap-12 items-center">
                {/* Left content */}
                <div className="text-center lg:text-left space-y-8 animate-fade-in">
                    <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-full text-primary text-sm font-medium">
                        <Sparkles className="w-4 h-4" />
                        AI-Powered Research Assistant
                    </div>

                    <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold leading-tight">
                        Your Intelligent
                        <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent"> Research Companion</span>
                    </h1>

                    <p className="text-xl text-muted-foreground max-w-2xl mx-[0px]">
                        Summarize, understand, and manage academic papers effortlessly.
                        Let AI transform how you interact with research.
                    </p>

                    <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
                        <Link to="/auth">
                            <Button size="lg" className="text-lg px-8 py-6 bg-primary hover:bg-primary-hover transition-all shadow-ai">
                                Get Started <ArrowRight className="ml-2 w-5 h-5" />
                            </Button>
                        </Link>
                        <Link to="/auth">
                            <Button size="lg" variant="outline" className="text-lg px-8 py-6 border-2">
                                Sign In
                            </Button>
                        </Link>
                    </div>

                    {/* Stats */}

                </div>

                {/* Right image */}
                <div className="relative animate-fade-in" style={{
                    animationDelay: '0.2s'
                }}>
                    <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-accent/20 rounded-3xl blur-2xl" />
                    <img src={heroImage} alt="AI Research Platform Interface" className="relative rounded-3xl shadow-2xl border border-border" />
                </div>
            </div>
        </div>
    </section>;
};
export default Hero;