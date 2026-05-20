import React from "react";
import { motion } from "framer-motion";
import ThreeDBackground from "../components/ThreeDBackground";
import AnimatedHero from "../components/AnimatedHero";
import AnimatedCard from "../components/AnimatedCard";

const launcherCards = [
    {
        title: "AI Based Stock Predictor",
        description: "Open the prediction flow and explore the forecast engine for a ticker.",
        to: "/predict",
        accent: "from-cyan-400/30 to-blue-500/20",
        border: "border-cyan-500/30",
        button: "Start Predicting",
    },
    {
        title: "Detailed Stock Analyser",
        description: "Jump straight to the search bar and inspect full company insights.",
        to: "/analyse",
        accent: "from-emerald-400/20 to-cyan-500/20",
        border: "border-emerald-500/30",
        button: "Open Search Bar",
    },
];

const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: {
            staggerChildren: 0.1,
        },
    },
};

export default function Home() {
    return (
        <>
            <ThreeDBackground />
            <main className="relative z-10 max-w-7xl mx-auto px-6 py-14 pb-40 md:py-20 md:pb-48 lg:pb-56">
                {/* Animated Hero Section */}
                <AnimatedHero />

                {/* Cards Section */}
                <motion.section
                    variants={containerVariants}
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true, amount: 0.2 }}
                    className="mt-20 grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto"
                >
                    {launcherCards.map((card, index) => (
                        <AnimatedCard key={card.title} card={card} index={index} />
                    ))}
                </motion.section>

                {/* Decorative elements */}
                <motion.div
                    className="mt-32 text-center"
                    initial={{ opacity: 0 }}
                    whileInView={{ opacity: 1 }}
                    transition={{ delay: 0.5, duration: 1 }}
                    viewport={{ once: true }}
                >
                    <p className="text-cyan-500/60 text-sm tracking-[0.3em] uppercase font-black">
                        Choose your path
                    </p>
                </motion.div>
            </main>
        </>
    );
}