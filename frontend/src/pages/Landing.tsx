import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import Features from "@/components/Features";
import Footer from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";
const Landing = () => {
    return <div className="min-h-screen">
        <Navbar />
        <Hero />
        <Features />


        {/* CTA Section */}
        <section className="py-24 bg-gradient-to-br from-primary to-accent text-white relative overflow-hidden">
            <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSAxMCAwIEwgMCAwIDAgMTAiIGZpbGw9Im5vbmUiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS1vcGFjaXR5PSIwLjEiIHN0cm9rZS13aWR0aD0iMSIvPjwvcGF0dGVybj48L2RlZnM+PHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0idXJsKCNncmlkKSIvPjwvc3ZnPg==')] opacity-20" />

            <div className="container mx-auto px-4 text-center relative z-10">
                <h2 className="text-4xl md:text-5xl font-bold mb-6">
                    Ready to Transform Your Research?
                </h2>
                <p className="text-xl mb-8 text-white/90 max-w-2xl mx-auto">
                    Join thousands of researchers who are already using Inquiro to accelerate their work.
                </p>
                <Link to="/auth">
                    <Button size="lg" variant="secondary" className="text-lg px-8 py-6 bg-white text-primary hover:bg-white/90">
                        Start Free Today <ArrowRight className="ml-2 w-5 h-5" />
                    </Button>
                </Link>
            </div>
        </section>

        <Footer />
    </div>;
};
export default Landing;