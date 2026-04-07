import React, { useState, useCallback, useRef, useEffect } from 'react';
import Header from './components/Header';
import ImageUpload from './components/ImageUpload';
import ProductPanel from './components/ProductPanel';
import ActionLog from './components/ActionLog';
import BeliefPanel from './components/BeliefPanel';
import VerdictPanel from './components/VerdictPanel';
import ControlBar from './components/ControlBar';
import BackgroundFX from './components/BackgroundFX';

const API = window.location.origin;

export default function App() {
  const [obs, setObs] = useState(null);
  const [state, setState] = useState(null);
  const [log, setLog] = useState([]);
  const [running, setRunning] = useState(false);
  const [done, setDone] = useState(false);
  const [productData, setProductData] = useState(null);
  const [difficulty, setDifficulty] = useState('medium');
  const [agentType, setAgentType] = useState('smart');
  const [totalReward, setTotalReward] = useState(0);
  const [rewardHistory, setRewardHistory] = useState([]);
  const [gradeResult, setGradeResult] = useState(null);

  // 🔥 RANDOM SEED INITIAL
  const [seed, setSeed] = useState(() => Math.floor(Math.random() * 100000));

  const [isResetting, setIsResetting] = useState(false);
  const runRef = useRef(false);

  const fetchState = useCallback(async () => {
    try {
      const r = await fetch(`${API}/state`);
      if (r.ok) {
        const d = await r.json();
        setState(d);
      }
    } catch {}
  }, []);

  const doReset = useCallback(async (pd = productData) => {
    setIsResetting(true);
    setDone(false);
    setLog([]);
    setTotalReward(0);
    setRewardHistory([]);
    setGradeResult(null);
    runRef.current = false;

    // 🔥 NEW RANDOM SEED EVERY RESET
    const newSeed = Math.floor(Math.random() * 100000);
    setSeed(newSeed);

    try {
      const r = await fetch(`${API}/reset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ seed: newSeed, difficulty, product_data: pd }),
      });

      const d = await r.json();
      setObs(d);

      setLog([
        {
          step: 0,
          action: 'RESET',
          result: 'Episode started. Begin auditing.',
          reward: 0,
        },
      ]);

      await fetchState();
    } catch (e) {
      console.error(e);
    } finally {
      setIsResetting(false);
    }
  }, [productData, difficulty, fetchState]);

  const doAgentStep = useCallback(async () => {
    try {
      const r = await fetch(`${API}/agent_step`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agent_type: agentType }),
      });

      const d = await r.json();

      setObs(d.observation);

      setTotalReward(p =>
        parseFloat((p + d.reward).toFixed(4))
      );

      setRewardHistory(prev => [
        ...prev,
        {
          step: d.observation.step_num,
          reward: d.reward,
          cumulative: parseFloat(
            (prev.reduce((a, b) => a + b.reward, 0) + d.reward).toFixed(4)
          ),
        },
      ]);

      setLog(prev => [
        ...prev,
        {
          step: d.observation.step_num,
          action: d.action_taken
            ? `${d.action_taken.action_type}${d.action_taken.parameter ? ':' + d.action_taken.parameter : ''}`
            : '—',
          result: d.observation.last_action_result,
          reward: d.reward,
        },
      ]);

      if (d.done) {
        setDone(true);
        runRef.current = false;
        await fetchState();
        await doGrade(d.observation);
      }

      return d.done;
    } catch (e) {
      console.error(e);
      return true;
    }
  }, [agentType, fetchState]);

  const doGrade = useCallback(async (currentObs) => {
    try {
      const harmfulKws = [
        'parabens','formaldehyde','lead','mercury','oxybenzone','bpa',
        'phthalates','triclosan','sodium lauryl sulfate','propylene glycol',
        'diethanolamine','petrolatum','aluminum','talc','synthetic fragrance',
        'coal tar','hydroquinone'
      ];

      const predicted_harmful =
        (currentObs?.visible_ingredients || []).filter(i =>
          harmfulKws.some(k => i.includes(k))
        );

      const lastResult = currentObs?.last_action_result || '';

      const verdict =
        lastResult.includes('SAFE') && !lastResult.includes('UNSAFE')
          ? 'SAFE'
          : lastResult.includes('UNSAFE')
          ? 'UNSAFE'
          : 'SAFE';

      const r = await fetch(`${API}/grade`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          predicted_harmful,
          risk_estimate: currentObs?.risk_estimate || 0,
          verdict,
        }),
      });

      const d = await r.json();
      setGradeResult(d);
    } catch {}
  }, []);

  const runAgent = useCallback(async () => {
    if (running || done) return;

    if (!obs) {
      await doReset();
      return;
    }

    setRunning(true);
    runRef.current = true;

    while (runRef.current) {
      const isDone = await doAgentStep();
      if (isDone) break;
      await new Promise(r => setTimeout(r, 700));
    }

    setRunning(false);
    runRef.current = false;
  }, [running, done, obs, doReset, doAgentStep]);

  const stopAgent = () => {
    runRef.current = false;
    setRunning(false);
  };

  useEffect(() => {
    doReset();
  }, []); // eslint-disable-line

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-deep)', position: 'relative' }}>
      <BackgroundFX />
      <div style={{ position: 'relative', zIndex: 1 }}>
        <Header
          running={running}
          done={done}
          totalReward={totalReward}
          stepNum={obs?.step_num || 0}
        />
        <div style={{ padding: '0 24px 16px' }}>
          <ImageUpload
            onProductExtracted={(pd) => {
              setProductData(pd);
              doReset(pd);
            }}
            difficulty={difficulty}
            setDifficulty={setDifficulty}
          />
        </div>
        <div style={{ padding: '0 24px 16px' }}>
          <ControlBar
            running={running}
            done={done}
            obs={obs}
            agentType={agentType}
            setAgentType={setAgentType}
            seed={seed}
            setSeed={setSeed}
            difficulty={difficulty}
            setDifficulty={setDifficulty}
            onRun={runAgent}
            onStop={stopAgent}
            onReset={() => doReset()}
            isResetting={isResetting}
          />
        </div>
        <div style={{
          display: 'grid',
          gridTemplateColumns: '300px 1fr 280px',
          gap: '16px',
          padding: '0 24px 16px'
        }}>
          <ProductPanel obs={obs} state={state} productData={productData} />
          <ActionLog log={log} running={running} rewardHistory={rewardHistory} />
          <BeliefPanel obs={obs} state={state} running={running} />
        </div>
        <div style={{ padding: '0 24px 32px' }}>
          <VerdictPanel
            obs={obs}
            state={state}
            done={done}
            gradeResult={gradeResult}
            rewardHistory={rewardHistory}
          />
        </div>
      </div>
    </div>
  );
}
