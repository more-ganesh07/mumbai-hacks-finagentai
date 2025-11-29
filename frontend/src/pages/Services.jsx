import React from "react";
import { motion } from "motion/react";
import {
    MessageSquare,
    BarChart3,
    FileText,
    TrendingUp,
    Shield,
    Zap,
    Clock,
    Brain,
    PieChart,
    LineChart,
    DollarSign,
    Bell
} from "lucide-react";
import PlainFooter from "../components/PlainFooter";
import "../styles/Services.css";

export default function Services() {
    const mainServices = [
        
        {
            icon: FileText,
            title: "Automated Report Generation",
            description: "Generate professional PDF reports in seconds. Perfect for clients, advisors, or personal record-keeping.",
            features: [
                "One-click PDF export",
                "Customizable templates",
                "Comprehensive insights",
                "Shareable reports"
            ],
            color: "#22d3ee"
        },
        {
            icon: MessageSquare,
            title: "AI-Powered Portfolio Conversation",
            description: "Have natural conversations with your portfolio. Ask questions in plain English and get instant, intelligent answers about your investments.",
            features: [
                "Natural language queries",
                "Real-time portfolio insights",
                "Personalized recommendations",
                "24/7 AI assistance"
            ],
            color: "#ff7a18"
        },
        {
            icon: BarChart3,
            title: "Advanced Analytics Dashboard",
            description: "Visualize your portfolio performance with stunning, interactive charts and comprehensive metrics that matter.",
            features: [
                "Real-time market data",
                "Performance tracking",
                "Risk analysis",
                "Asset allocation views"
            ],
            color: "#a78bfa"
        },
    ];

    const additionalFeatures = [
        {
            icon: TrendingUp,
            title: "Market Trend Analysis",
            description: "Stay ahead with AI-powered market trend predictions and sector analysis."
        },
        {
            icon: MessageSquare,
            title: "Portfolio Chat Insights",
            description: "Ask questions about your portfolio in natural language and get instant, intelligent responses from our AI."
        },
        {
            icon: FileText,
            title: "Instant Report Generation",
            description: "Create professional, comprehensive portfolio reports in seconds with one-click PDF export."
        },
        {
            icon: DollarSign,
            title: "Performance Tracking",
            description: "Monitor returns, dividends, and overall portfolio growth over time."
        }
    ];

    const pricingPlans = [
        {
            name: "Free",
            price: "₹0",
            period: "forever",
            features: [
                "Basic portfolio chat",
                "Up to 10 holdings",
                "Monthly reports",
                "Email support"
            ],
            cta: "Get Started",
            popular: false
        },
        {
            name: "Pro",
            price: "₹999",
            period: "per month",
            features: [
                "Unlimited portfolio chat",
                "Unlimited holdings",
                "Daily reports",
                "Advanced analytics",
                "Priority support",
                "Custom alerts"
            ],
            cta: "Start Free Trial",
            popular: true
        },
        {
            name: "Enterprise",
            price: "Custom",
            period: "contact us",
            features: [
                "Everything in Pro",
                "Multi-user access",
                "API access",
                "Dedicated support",
                "Custom integrations",
                "White-label options"
            ],
            cta: "Contact Sales",
            popular: false
        }
    ];

    return (
        <div className="services-page">
            {/* Hero Section */}
            <section className="services-hero">
                <div className="services-hero-content">
                    <motion.h1
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6 }}
                        className="services-hero-title"
                    >
                        Our <span className="brand-glow">Services</span>
                    </motion.h1>
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 0.2 }}
                        className="services-hero-subtitle"
                    >
                        Comprehensive AI-powered tools to manage and grow your investments
                    </motion.p>
                </div>

                {/* Animated icons */}
                <div className="hero-icons">
                    <motion.div
                        animate={{ y: [0, -10, 0] }}
                        transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                        className="floating-icon icon-1"
                    >
                        <Zap size={32} color="#ff7a18" />
                    </motion.div>
                    <motion.div
                        animate={{ y: [0, -15, 0] }}
                        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut", delay: 1 }}
                        className="floating-icon icon-2"
                    >
                        <LineChart size={32} color="#a78bfa" />
                    </motion.div>
                    <motion.div
                        animate={{ y: [0, -12, 0] }}
                        transition={{ duration: 3.5, repeat: Infinity, ease: "easeInOut", delay: 2 }}
                        className="floating-icon icon-3"
                    >
                        <Clock size={32} color="#22d3ee" />
                    </motion.div>
                </div>
            </section>

            {/* Main Services */}
            <section className="main-services">
                <div className="services-container">
                    {mainServices.map((service, index) => {
                        const Icon = service.icon;
                        return (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, y: 30 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ duration: 0.5, delay: index * 0.15 }}
                                className="service-card-large"
                            >
                                <div className="service-header">
                                    <div
                                        className="service-icon-large"
                                        style={{
                                            background: `linear-gradient(135deg, ${service.color}22, ${service.color}11)`,
                                            border: `1px solid ${service.color}44`
                                        }}
                                    >
                                        <Icon size={36} color={service.color} />
                                    </div>
                                    <h3 className="service-title-large">{service.title}</h3>
                                </div>
                                <p className="service-description">{service.description}</p>
                                <ul className="service-features">
                                    {service.features.map((feature, idx) => (
                                        <li key={idx} className="feature-item">
                                            <span className="feature-bullet" style={{ background: service.color }}></span>
                                            {feature}
                                        </li>
                                    ))}
                                </ul>
                            </motion.div>
                        );
                    })}
                </div>
            </section>

            {/* Additional Features */}
            <section className="additional-features">
                <h2 className="section-title">More Powerful Features</h2>
                <div className="features-grid">
                    {additionalFeatures.map((feature, index) => {
                        const Icon = feature.icon;
                        return (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, scale: 0.9 }}
                                whileInView={{ opacity: 1, scale: 1 }}
                                viewport={{ once: true }}
                                transition={{ duration: 0.4, delay: index * 0.08 }}
                                className="feature-card-small"
                            >
                                <div className="feature-icon-small">
                                    <Icon size={24} />
                                </div>
                                <h4 className="feature-title-small">{feature.title}</h4>
                                <p className="feature-description-small">{feature.description}</p>
                            </motion.div>
                        );
                    })}
                </div>
            </section>

            {/* Pricing Section */}
            <section id="pricing" className="pricing-section">
                <h2 className="section-title">Choose Your Plan</h2>
                <p className="pricing-subtitle">
                    Start free, upgrade when you need more power
                </p>
                <div className="pricing-grid">
                    {pricingPlans.map((plan, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.5, delay: index * 0.1 }}
                            className={`pricing-card ${plan.popular ? "popular" : ""}`}
                        >
                            {plan.popular && <div className="popular-badge">Most Popular</div>}
                            <h3 className="plan-name">{plan.name}</h3>
                            <div className="plan-price">
                                <span className="price">{plan.price}</span>
                                <span className="period">/{plan.period}</span>
                            </div>
                            <ul className="plan-features">
                                {plan.features.map((feature, idx) => (
                                    <li key={idx} className="plan-feature">
                                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                            <circle cx="10" cy="10" r="10" fill="#22c55e22" />
                                            <path
                                                d="M6 10l2.5 2.5L14 7"
                                                stroke="#22c55e"
                                                strokeWidth="2"
                                                strokeLinecap="round"
                                                strokeLinejoin="round"
                                            />
                                        </svg>
                                        {feature}
                                    </li>
                                ))}
                            </ul>
                            <button
                                className={`plan-button ${plan.popular ? "popular-button" : ""}`}
                                onClick={() => window.location.href = "/login"}
                            >
                                {plan.cta}
                            </button>
                        </motion.div>
                    ))}
                </div>
            </section>

            {/* CTA Section */}
            <section className="services-cta">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6 }}
                    className="cta-content"
                >
                    <h2 className="cta-title">Ready to Experience the Future of Portfolio Management?</h2>
                    <p className="cta-subtitle">
                        Join thousands of smart investors using FinAgentAI
                    </p>
                    <button className="cta-button" onClick={() => window.location.href = "/login"}>
                        Start Your Free Trial
                    </button>
                </motion.div>
            </section>

            <PlainFooter />
        </div>
    );
}
