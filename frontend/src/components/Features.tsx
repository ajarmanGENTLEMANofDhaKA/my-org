import { FileText, MessageSquare, Globe, Lightbulb, FolderTree, Zap } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import featureAI from "@/assets/feature-ai.jpg";
import featureOrganize from "@/assets/feature-organize.jpg";
import featureChat from "@/assets/feature-chat.jpg";

const Features = () => {
  const features = [
    {
      icon: FileText,
      image: featureAI,
      title: "AI Summaries",
      description: "Instantly generate comprehensive summaries of complex academic papers with advanced AI technology."
    },
    {
      icon: MessageSquare,
      image: featureChat,
      title: "Chat with Papers",
      description: "Ask questions and get instant answers from your research papers using conversational AI."
    },
    {
      icon: FolderTree,
      image: featureOrganize,
      title: "Smart Organization",
      description: "Organize papers into workspaces with intelligent categorization and easy retrieval."
    },
    {
      icon: Globe,
      title: "Multi-Language Translation",
      description: "Translate research papers and excerpts into multiple languages seamlessly."
    },
    {
      icon: Lightbulb,
      title: "Contextual Explanations",
      description: "Highlight any text to get detailed explanations and context from AI."
    },
    {
      icon: Zap,
      title: "Lightning Fast",
      description: "Process and analyze papers in seconds with optimized AI algorithms."
    }
  ];

  return (
    <section id="features" className="py-24 bg-secondary/50">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16 space-y-4 animate-fade-in">
          <h2 className="text-4xl md:text-5xl font-bold">
            Powerful Features for
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent"> Modern Research</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Everything you need to manage, understand, and interact with academic papers efficiently.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <Card 
                key={index} 
                className="group hover:shadow-lg transition-all duration-300 hover:-translate-y-1 border-border/50 bg-gradient-card animate-fade-in"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <CardContent className="p-6 space-y-4">
                  {feature.image ? (
                    <div className="w-16 h-16 rounded-2xl overflow-hidden mb-4 ring-2 ring-primary/20 group-hover:ring-primary/40 transition-all">
                      <img src={feature.image} alt={feature.title} className="w-full h-full object-cover" />
                    </div>
                  ) : (
                    <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary to-accent flex items-center justify-center group-hover:scale-110 transition-transform">
                      <Icon className="w-8 h-8 text-white" />
                    </div>
                  )}
                  
                  <h3 className="text-xl font-semibold group-hover:text-primary transition-colors">
                    {feature.title}
                  </h3>
                  <p className="text-muted-foreground leading-relaxed">
                    {feature.description}
                  </p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default Features;
