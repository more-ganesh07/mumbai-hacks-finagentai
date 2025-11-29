import React from 'react';
import { motion } from 'motion/react';
import { CheckCircle2, PieChart, TrendingUp } from 'lucide-react';
import './FeatureBlocks.css';

const FeatureBlocks = () => {
  return (
    <div className="feature-blocks-container">
      {/* Block 1: Analytics Dashboard */}
      <div className="feature-row">
        <div className="feature-visual">
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1.5fr 1fr',
            gridTemplateRows: '1fr 1fr',
            gap: '12px',
            width: '90%',
            height: '80%'
          }}>
            {/* Widget 1: Bar Chart */}
            <div style={{
              gridRow: '1 / -1',
              background: 'rgba(255,255,255,0.03)',
              borderRadius: '12px',
              padding: '16px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              border: '1px solid rgba(255,255,255,0.08)'
            }}>
              <div style={{ fontSize: '0.8rem', color: '#9ca3af', marginBottom: '8px' }}>Performance</div>
              <div style={{ display: 'flex', alignItems: 'flex-end', gap: '8px', height: '100%' }}>
                {[1, 2, 3, 4, 5].map((i) => (
                  <motion.div
                    key={i}
                    initial={{ height: '20%' }}
                    animate={{ height: ['20%', '60%', '40%', '80%', '50%'] }}
                    transition={{
                      duration: 3,
                      repeat: Infinity,
                      repeatType: "reverse",
                      delay: i * 0.1,
                      ease: "easeInOut"
                    }}
                    style={{
                      flex: 1,
                      background: 'linear-gradient(to top, var(--accent-orange), #ffb74d)',
                      borderRadius: '4px',
                      opacity: 0.8
                    }}
                  />
                ))}
              </div>
            </div>

            {/* Widget 2: Pie Chart */}
            <div style={{
              background: 'rgba(255,255,255,0.03)',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '1px solid rgba(255,255,255,0.08)',
              position: 'relative'
            }}>
              <div style={{
                width: '50px',
                height: '50px',
                borderRadius: '50%',
                background: 'conic-gradient(var(--accent-orange) 0% 65%, #a78bfa 65% 85%, #22d3ee 85% 100%)',
                position: 'relative'
              }}>
                <div style={{ position: 'absolute', inset: '12px', background: '#1b2440', borderRadius: '50%' }} />
              </div>
              <span style={{ position: 'absolute', bottom: '8px', fontSize: '0.65rem', color: '#9ca3af' }}>Alloc</span>
            </div>

            {/* Widget 3: Stat Card */}
            <div style={{
              background: 'rgba(255,255,255,0.03)',
              borderRadius: '12px',
              padding: '12px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              border: '1px solid rgba(255,255,255,0.08)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
                <TrendingUp size={14} color="#22c55e" />
                <span style={{ fontSize: '0.75rem', color: '#9ca3af' }}>Return</span>
              </div>
              <span style={{ fontSize: '1.1rem', fontWeight: 'bold', color: '#fff' }}>+24.8%</span>
            </div>
          </div>
        </div>
        <div className="feature-content">
          <h2 className="feature-title">Deep Portfolio Analytics</h2>
          <p className="feature-desc">
            Visualize your asset allocation and performance trends with crystal clarity.
            Our AI digests complex data into simple, actionable charts that help you make smarter decisions.
          </p>
        </div>
      </div>

      {/* Block 2: NLP Chat */}
      <div className="feature-row reverse">
        <div className="feature-visual">
          <div style={{ position: 'relative', width: '100%', height: '100%', padding: '20px' }}>
            {/* Msg 1: User */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0 }}
              style={{
                position: 'absolute',
                top: '10%',
                left: '10%',
                background: 'rgba(255,255,255,0.1)',
                padding: '10px 16px',
                borderRadius: '12px 12px 12px 0',
                border: '1px solid rgba(255,255,255,0.1)',
                maxWidth: '200px'
              }}
            >
              <span style={{ color: '#fff', fontSize: '0.85rem' }}>How's my tech sector?</span>
            </motion.div>

            {/* Msg 2: Bot */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 1.2 }}
              style={{
                position: 'absolute',
                top: '32%',
                right: '10%',
                background: '#ffb74d',
                padding: '10px 16px',
                borderRadius: '12px 12px 0 12px',
                color: '#000',
                maxWidth: '200px'
              }}
            >
              <span style={{ fontSize: '0.85rem', fontWeight: '600' }}>Up 12% this month! 🚀</span>
            </motion.div>

            {/* Msg 3: User */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 2.5 }}
              style={{
                position: 'absolute',
                top: '54%',
                left: '10%',
                background: 'rgba(255,255,255,0.1)',
                padding: '10px 16px',
                borderRadius: '12px 12px 12px 0',
                border: '1px solid rgba(255,255,255,0.1)',
                maxWidth: '200px'
              }}
            >
              <span style={{ color: '#fff', fontSize: '0.85rem' }}>What about risk?</span>
            </motion.div>

            {/* Msg 4: Bot */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 3.8 }}
              style={{
                position: 'absolute',
                top: '76%',
                right: '10%',
                background: '#ffb74d',
                padding: '10px 16px',
                borderRadius: '12px 12px 0 12px',
                color: '#000',
                maxWidth: '200px'
              }}
            >
              <span style={{ fontSize: '0.85rem', fontWeight: '600' }}>Sharpe ratio is 1.8 (Healthy) ✅</span>
            </motion.div>
          </div>
        </div>
        <div className="feature-content">
          <h2 className="feature-title">Natural Language Queries</h2>
          <p className="feature-desc">
            Just ask, "How is my tech sector doing?" and get an instant answer.
            No more digging through spreadsheets or complex dashboards—just chat with your portfolio.
          </p>
        </div>
      </div>

      {/* Block 3: Reporting */}
      <div className="feature-row">
        <div className="feature-visual">
          <motion.div
            initial={{ scale: 0.95, opacity: 0.9 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 2, repeat: Infinity, repeatType: "reverse" }}
            style={{
              background: '#1e293b',
              width: '180px',
              height: '240px',
              borderRadius: '12px',
              border: '1px solid rgba(255,255,255,0.1)',
              display: 'flex',
              flexDirection: 'column',
              padding: '20px',
              boxShadow: '0 10px 30px rgba(0,0,0,0.3)',
              position: 'relative'
            }}
          >
            {/* Doc Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <div style={{ width: '40%', height: '8px', background: 'rgba(255,255,255,0.3)', borderRadius: '4px' }} />
              <div style={{ width: '20%', height: '8px', background: 'rgba(255,255,255,0.1)', borderRadius: '4px' }} />
            </div>

            {/* Graph in Report */}
            <div style={{
              width: '100%',
              height: '70px',
              background: 'rgba(0,0,0,0.2)',
              borderRadius: '8px',
              marginBottom: '16px',
              overflow: 'hidden',
              position: 'relative'
            }}>
              <svg viewBox="0 0 100 40" width="100%" height="100%" preserveAspectRatio="none" style={{ display: 'block' }}>
                <path d="M0,40 Q20,35 40,15 T100,20 V40 H0 Z" fill="var(--accent-orange)" opacity="0.2" />
                <path d="M0,40 Q20,35 40,15 T100,20" fill="none" stroke="var(--accent-orange)" strokeWidth="2" />
              </svg>
            </div>

            {/* Text Lines */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px' }} />
              <div style={{ width: '92%', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px' }} />
              <div style={{ width: '96%', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px' }} />
              <div style={{ width: '80%', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px' }} />
            </div>

            {/* Success Badge */}
            <motion.div
              initial={{ scale: 0, rotate: -45 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ delay: 0.5, type: 'spring', stiffness: 200, damping: 15 }}
              style={{
                position: 'absolute',
                bottom: '16px',
                right: '16px',
                background: '#22c55e',
                borderRadius: '50%',
                padding: '6px',
                display: 'flex',
                boxShadow: '0 4px 12px rgba(34, 197, 94, 0.4)'
              }}
            >
              <CheckCircle2 size={20} color="#fff" />
            </motion.div>
          </motion.div>
        </div>
        <div className="feature-content">
          <h2 className="feature-title">Automated Reporting</h2>
          <p className="feature-desc">
            Generate comprehensive PDF reports for your clients or personal records in seconds.
            Professional, accurate, and effortless—ready to share at a moment's notice.
          </p>
        </div>
      </div>
    </div>
  );
};

export default FeatureBlocks;
