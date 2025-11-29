import React from "react";
import { motion } from "motion/react";
import { Target, Users, Zap, Award, TrendingUp, Shield } from "lucide-react";
import PlainFooter from "../components/PlainFooter";
import "../styles/About.css";

export default function About() {
    const values = [
        {
            icon: Target,
            title: "Mission-Driven",
            description: "Empowering investors with AI-powered insights to make smarter financial decisions."
        },
        {
            icon: Shield,
            title: "Trust & Security",
            description: "Your data security is our top priority. We use industry-leading encryption and security practices."
        },
        {
            icon: Zap,
            title: "Innovation First",
            description: "Constantly evolving our AI models to provide cutting-edge market intelligence."
        },
        {
            icon: Award,
            title: "Excellence",
            description: "Committed to delivering exceptional quality in every feature and interaction."
        }
    ];

    const team = [
        {
            name: "Ganesh More",
            role: "Backend Developer",
            initials: "GM",
            color: "#ff7a18"
        },
        {
            name: "Hrishikesh Bhogade",
            role: "UI/UX Designer",
            initials: "HB",
            color: "#a78bfa"
        }
    ];

    return (
        <div className="about-page">
            {/* Hero Section */}
            <section className="about-hero">
                <div className="about-hero-content">
                    <motion.h1
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6 }}
                        className="about-hero-title"
                    >
                        About <span className="brand-glow">FinAgentAI</span>
                    </motion.h1>
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 0.2 }}
                        className="about-hero-subtitle"
                    >
                        Revolutionizing portfolio management with artificial intelligence
                    </motion.p>
                </div>

                {/* Animated background elements */}
                <div className="about-hero-bg">
                    <div className="floating-orb orb-1"></div>
                    <div className="floating-orb orb-2"></div>
                    <div className="floating-orb orb-3"></div>
                </div>
            </section>

            {/* Story Section */}
            <section className="about-story">
                <div className="story-container">
                    <motion.div
                        initial={{ opacity: 0, x: -30 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6 }}
                        className="story-content"
                    >
                        <h2 className="section-title">Our Story</h2>
                        <p className="story-text">
                            FinAgentAI was born from a simple observation: managing investments shouldn't require
                            a finance degree. In 2024, our founders—seasoned developers and financial analysts—came
                            together with a vision to democratize portfolio management.
                        </p>
                        <p className="story-text">
                            We built an AI-powered platform that speaks your language. No complex jargon, no
                            overwhelming dashboards—just clear insights, intelligent analysis, and actionable
                            recommendations. Today, we're proud to serve thousands of investors who trust us
                            with their financial future.
                        </p>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, x: 30 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6 }}
                        className="story-visual"
                    >
                        <div className="visual-grid">
                            <div className="visual-item item-1">
                                <TrendingUp size={32} color="#ff7a18" />
                                <span>Intelligent Analytics</span>
                            </div>
                            <div className="visual-item item-2">
                                <Users size={32} color="#a78bfa" />
                                <span>AI-Powered Interactions</span>
                            </div>
                            <div className="visual-item item-3">
                                <Shield size={32} color="#22d3ee" />
                                <span>Bank-Grade Security</span>
                            </div>
                            <div className="visual-item item-4">
                                <Zap size={32} color="#fb7185" />
                                <span>Real-Time Insights</span>
                            </div>
                        </div>
                    </motion.div>
                </div>
            </section>

            {/* Values Section */}
            <section className="about-values">
                <h2 className="section-title">Our Core Values</h2>
                <div className="values-grid">
                    {values.map((value, index) => {
                        const Icon = value.icon;
                        return (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ duration: 0.5, delay: index * 0.1 }}
                                className="value-card"
                            >
                                <div className="value-icon">
                                    <Icon size={28} />
                                </div>
                                <h3 className="value-title">{value.title}</h3>
                                <p className="value-description">{value.description}</p>
                            </motion.div>
                        );
                    })}
                </div>
            </section>

            {/* Team Section */}
            <section className="about-team">
                <h2 className="section-title">Meet Our Team</h2>
                <p className="team-subtitle">
                    The brilliant minds behind FinAgentAI
                </p>
                <div className="team-grid">
                    {team.map((member, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, scale: 0.9 }}
                            whileInView={{ opacity: 1, scale: 1 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.4, delay: index * 0.1 }}
                            className="team-card"
                        >
                            <div
                                className="team-avatar"
                                style={{
                                    background: `linear-gradient(135deg, ${member.color}22, ${member.color}11)`,
                                    border: `2px solid ${member.color}44`
                                }}
                            >
                                <span style={{ color: member.color }}>{member.initials}</span>
                            </div>
                            <h3 className="team-name">{member.name}</h3>
                            <p className="team-role">{member.role}</p>
                        </motion.div>
                    ))}
                </div>
            </section>

            {/* CTA Section */}
            <section className="about-cta">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6 }}
                    className="cta-content"
                >
                    <h2 className="cta-title">Ready to Transform Your Portfolio?</h2>
                    <p className="cta-subtitle">
                        Join thousands of investors who trust FinAgentAI for smarter financial decisions
                    </p>
                    <button className="cta-button" onClick={() => window.location.href = "/login"}>
                        Get Started Today
                    </button>
                </motion.div>
            </section>

            <PlainFooter />
        </div>
    );
}
