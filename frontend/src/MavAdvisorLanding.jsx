import React, { useMemo } from "react";
import { motion, useScroll, useTransform } from "framer-motion";

const MavAdvisorLanding = () => {
  const { scrollYProgress } = useScroll();
  const bagOpen = useTransform(scrollYProgress, [0.08, 0.24], [0, 1], { clamp: false });
  const tabletRise = useTransform(scrollYProgress, [0.15, 0.35], [60, -120]);
  const tabletScale = useTransform(scrollYProgress, [0.35, 0.55], [0.8, 1.02]);
  const tabletGlow = useTransform(scrollYProgress, [0.20, 0.50], [0, 0.8]);
  const viewportOpacity = useTransform(scrollYProgress, [0.55, 0.65], [0, 1]);

  const cards = useMemo(
    () => [
      { title: "Degree Progress", color: "from-blue-400 to-blue-500" },
      { title: "Recommended Courses", color: "from-teal-400 to-teal-500" },
      { title: "AI Advisor Chat", color: "from-purple-400 to-purple-500" },
      { title: "Clubs & Opportunities", color: "from-amber-400 to-amber-500" },
    ],
    []
  );

  return (
    <div className="relative min-h-screen bg-gradient-to-b from-sky-50 via-white to-emerald-50 text-slate-800 overflow-x-hidden">
      <div className="pointer-events-none fixed top-0 left-0 w-full h-20 bg-white/70 backdrop-blur-md z-50 flex items-center justify-center">
        <div className="font-extrabold text-lg tracking-widest text-slate-700 uppercase">MavAdvisor</div>
      </div>

      <section className="relative min-h-screen flex items-center justify-center px-5 py-24 sm:py-36">
        <div className="max-w-3xl text-center">
          <motion.h1
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.1, duration: 0.8, ease: "easeOut" }}
            className="text-4xl sm:text-5xl md:text-6xl font-bold leading-tight text-slate-900"
          >
            Your advisor, right in your backpack
          </motion.h1>
          <motion.p
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.8, ease: "easeOut" }}
            className="mt-6 text-lg sm:text-xl text-slate-600"
          >
            Academic planning that moves with you
          </motion.p>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5, duration: 0.8 }}
            className="mt-10 text-sm uppercase tracking-wider text-slate-500"
          >
            Scroll to begin
          </motion.div>
        </div>
      </section>

      <section
        className="relative min-h-[190vh] flex items-start justify-center overflow-hidden pb-64"
        style={{ background: "linear-gradient(180deg, rgba(255,255,255,0) 0%, rgba(236,252,255,0.75) 30%, #f8fafc 100%)" }}
      >
        <motion.div
          style={{ translateY: tabletRise, scale: tabletScale }}
          className="relative w-[280px] sm:w-[360px] md:w-[420px] mt-24"
        >
          <motion.div
            style={{ opacity: tabletGlow }}
            className="absolute inset-0 rounded-3xl bg-cyan-300/30 blur-[18px] pointer-events-none"
          />
          <div className="relative z-20">
            <motion.div
              style={{ height: bagOpen }}
              className="rounded-t-[140px] bg-gradient-to-br from-stone-200 to-stone-300 w-full h-8 overflow-hidden origin-top"
            />
            <div className="relative rounded-b-2xl rounded-t-xl bg-stone-200 px-4 py-9 shadow-lg border border-stone-300">
              <div className="h-20 rounded-xl bg-gradient-to-br from-stone-300 via-stone-200 to-stone-300 border border-stone-400" />
              <div className="mt-5 flex justify-between">
                <div className="h-4 w-16 bg-stone-400 rounded-full" />
                <div className="h-4 w-8 bg-stone-400 rounded-full" />
              </div>
            </div>

            <motion.div
              style={{
                translateY: useTransform(scrollYProgress, [0.08, 0.35], [120, -22]),
                opacity: useTransform(scrollYProgress, [0.08, 0.25], [0.4, 1]),
              }}
              className="absolute left-1/2 top-[-16px] -translate-x-1/2 w-[220px] sm:w-[280px] md:w-[330px]"
            >
              <div className="relative h-[360px] sm:h-[420px] w-full rounded-3xl bg-gradient-to-br from-slate-50 via-white to-slate-100 border border-slate-300 shadow-2xl overflow-hidden">
                <div className="absolute inset-0 bg-black/0 pointer-events-none" />
                <motion.div
                  style={{
                    opacity: useTransform(scrollYProgress, [0.12, 0.28, 0.45], [0, 1, 0.8]),
                    scale: useTransform(scrollYProgress, [0.12, 0.36, 0.5], [0.95, 1, 1.04]),
                    translateY: useTransform(scrollYProgress, [0.12, 0.3], [40, 0]),
                  }}
                  className="relative h-full bg-gradient-to-br from-white via-sky-50 to-cyan-50 p-4"
                >
                  <div className="absolute inset-0 rounded-3xl border border-sky-100 ring-1 ring-sky-100" />
                  <div className="relative z-10 h-full flex flex-col gap-3">
                    <div className="h-10 rounded-2xl border border-slate-200 bg-white/90 flex items-center px-3 text-sm text-slate-500">MavAdvisor • Student Dashboard</div>
                    <div className="grid grid-cols-2 gap-3 mt-2">
                      {cards.map((card) => (
                        <motion.div
                          key={card.title}
                          initial={{ y: 20, opacity: 0 }}
                          animate={{ y: 0, opacity: 1 }}
                          transition={{ duration: 0.6, ease: "easeOut" }}
                          className={`rounded-xl p-3 bg-gradient-to-r ${card.color} text-white shadow`}
                        >
                          <p className="text-xs uppercase tracking-wider opacity-80">{card.title}</p>
                          <div className="mt-2 h-6 w-16 rounded-lg bg-white/25 animate-pulse" />
                        </motion.div>
                      ))}
                    </div>
                    <div className="mt-auto rounded-xl border border-slate-200 bg-white/80 p-3">
                      <div className="font-semibold text-sm text-slate-700">Next milestone</div>
                      <div className="text-xs text-slate-500 mt-1">Finish 4 credits foundation track</div>
                    </div>
                  </div>
                </motion.div>
              </div>
            </motion.div>
          </div>
        </motion.div>

        <div className="absolute top-[25%] left-1/2 w-full max-w-3xl -translate-x-1/2 pointer-events-none text-center">
          <motion.p
            style={{
              opacity: useTransform(scrollYProgress, [0.22, 0.32], [0, 1]),
              y: useTransform(scrollYProgress, [0.22, 0.32], [20, 0]),
            }}
            className="text-lg sm:text-2xl font-semibold text-slate-700 mb-2"
          >
            College is already a lot to carry.
          </motion.p>
          <motion.p
            style={{
              opacity: useTransform(scrollYProgress, [0.32, 0.44], [0, 1]),
              y: useTransform(scrollYProgress, [0.32, 0.44], [20, 0]),
            }}
            className="text-lg sm:text-2xl font-semibold text-slate-700 mb-2"
          >
            Planning your path should not be.
          </motion.p>
          <motion.p
            style={{
              opacity: useTransform(scrollYProgress, [0.44, 0.58], [0, 1]),
              y: useTransform(scrollYProgress, [0.44, 0.58], [20, 0]),
            }}
            className="text-lg sm:text-2xl font-semibold text-slate-700"
          >
            Meet MavAdvisor.
          </motion.p>
        </div>

        <motion.div className="absolute inset-x-0 top-[65%] z-10 px-6" style={{ opacity: viewportOpacity }}>
          <div className="mx-auto max-w-3xl rounded-3xl bg-white/90 shadow-2xl border border-slate-100 p-8">
            <div className="text-center mb-6">
              <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900">Welcome to MavAdvisor</h2>
              <p className="mt-3 text-base sm:text-lg text-slate-600">Your personalized academic planning companion.</p>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <button className="rounded-xl py-3 text-base font-bold text-white bg-blue-500 hover:bg-blue-600 transition">Login</button>
              <button className="rounded-xl py-3 text-base font-bold text-white bg-emerald-500 hover:bg-emerald-600 transition">Register</button>
            </div>
          </div>
        </motion.div>
      </section>

      <div className="absolute inset-x-0 bottom-12 text-center text-sm text-slate-500">
        <p>Scroll down to discover your academic path.</p>
      </div>
    </div>
  );
};

export default MavAdvisorLanding;
