import { Button } from "@/components/ui/button";
import { BookOpen, Menu, X } from "lucide-react";
import { Link } from "react-router-dom";
import { useState } from "react";
const Navbar = () => {
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    return <nav className="sticky top-0 z-50 bg-background/80 backdrop-blur-lg border-b border-border">
        <div className="container mx-auto px-4">
            <div className="flex items-center justify-between h-16">
                {/* Logo */}
                <Link to="/" className="flex items-center gap-2 group">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center group-hover:scale-110 transition-transform">
                        <BookOpen className="w-6 h-6 text-white" />
                    </div>
                    <span className="text-2xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                        Inquiro
                    </span>
                </Link>

                {/* Desktop Navigation */}
                <div className="hidden md:flex items-center gap-8">
                    <a href="#features" className="text-foreground hover:text-primary transition-colors">
                        Features
                    </a>
                    <Link to="/auth">
                        <Button variant="outline" className="border-primary text-primary hover:bg-primary hover:text-white">
                            Sign In
                        </Button>
                    </Link>
                    <Link to="/auth">
                        <Button className="bg-primary hover:bg-primary-hover">
                            Get Started
                        </Button>
                    </Link>
                </div>

                {/* Mobile menu button */}
                <button className="md:hidden p-2" onClick={() => setIsMenuOpen(!isMenuOpen)}>
                    {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                </button>
            </div>

            {/* Mobile menu */}
            {isMenuOpen && <div className="md:hidden py-4 space-y-4 border-t border-border">
                <a href="#features" className="block py-2 text-foreground hover:text-primary transition-colors" onClick={() => setIsMenuOpen(false)}>
                    Features
                </a>
                <Link to="/auth" onClick={() => setIsMenuOpen(false)}>
                    <Button variant="outline" className="w-full mb-2">
                        Sign In
                    </Button>
                </Link>
                <Link to="/auth" onClick={() => setIsMenuOpen(false)}>
                    <Button className="w-full bg-primary hover:bg-primary-hover">
                        Get Started
                    </Button>
                </Link>
            </div>}
        </div>
    </nav>;
};
export default Navbar;