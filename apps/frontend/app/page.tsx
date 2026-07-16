"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";

/* ─────────────────────────────────────────────
   Dados estáticos — equivalentes às seções do Zite
───────────────────────────────────────────────*/
const howItWorks = [
  {
    num: "1",
    title: "Faça sua pergunta, na hora",
    desc: "Descreva o que você precisa em linguagem natural. Sem comandos complexos, sem curva de aprendizado.",
  },
  {
    num: "2",
    title: "Conecte seu contexto com segurança",
    desc: "O agente usa o histórico da sua conversa para gerar respostas mais precisas e personalizadas.",
  },
  {
    num: "3",
    title: "Produza de qualquer lugar",
    desc: "Use pelo browser ou via CLI no terminal. O mesmo agente, onde você estiver, sem perder contexto.",
  },
];

const whyCards = [
  {
    title: "Entenda como suas conversas funcionam",
    desc: "Histórico completo de interações, sem caixas-pretas. Você vê e controla tudo.",
  },
  {
    title: "Deixe seu time usar com segurança",
    desc: "Controle de acesso por conta, com autenticação segura via cookie HttpOnly.",
  },
  {
    title: "Limite o acesso com permissões",
    desc: "Defina quem pode usar o agente e o que cada usuário pode fazer dentro do sistema.",
  },
];

const features = [
  {
    title: "Login seguro integrado",
    desc: "Autenticação via e-mail e senha com sessões protegidas por cookie HttpOnly.",
  },
  {
    title: "Banco de dados sem limite de usuários",
    desc: "PostgreSQL gerenciado, pronto para escalar sem custo extra por usuário.",
  },
  {
    title: "Terminal e Web",
    desc: "CLI no terminal para devs e interface web para qualquer pessoa do time.",
  },
  {
    title: "Contexto persistente",
    desc: "O agente lembra o que foi dito e usa isso para respostas mais relevantes.",
  },
  {
    title: "Segurança em primeiro lugar",
    desc: "Sessões criptografadas, tokens em hash e arquitetura preparada para produção.",
  },
  {
    title: "Open e extensível",
    desc: "Backend em Python/FastAPI. Fácil de customizar, integrar e evoluir.",
  },
];

/* ─────────────────────────────────────────────
   Componente principal
───────────────────────────────────────────────*/
export default function LandingPage() {
  const [input, setInput] = useState("");
  const [scrolled, setScrolled] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    router.push("/login");
  }

  return (
    <div className="min-h-screen bg-white text-[#0a0a14] font-sans">

      {/* ── NAVBAR ─────────────────────────────── */}
      <header
        className={`fixed top-0 inset-x-0 z-50 transition-all duration-200 ${
          scrolled ? "bg-white/95 backdrop-blur-sm shadow-[0_1px_0_0_#e5e7eb]" : "bg-white"
        }`}
      >
        <div className="mx-auto max-w-[1200px] px-6 h-[60px] flex items-center justify-between">
          <span className="font-bold text-[17px] tracking-tight">Terminal Agent</span>

          <nav className="hidden md:flex items-center gap-7">
            <a href="#como-funciona" className="text-sm text-[#444] hover:text-[#0a0a14] transition-colors">
              Como funciona
            </a>
            <a href="#funcionalidades" className="text-sm text-[#444] hover:text-[#0a0a14] transition-colors">
              Funcionalidades
            </a>
            <a href="#por-que" className="text-sm text-[#444] hover:text-[#0a0a14] transition-colors">
              Por que usar
            </a>
          </nav>

          <div className="flex items-center gap-2">
            <Link href="/login">
              <Button variant="ghost" size="sm" className="text-sm px-4 h-9 font-normal">
                Entrar
              </Button>
            </Link>
            <Link href="/register">
              <Button size="sm" className="text-sm px-5 h-9">
                Criar conta
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* ── HERO ───────────────────────────────── */}
      <section className="pt-[110px] pb-10 px-6 text-center flex flex-col items-center">
        <span className="inline-flex items-center gap-1.5 text-[11px] font-semibold tracking-[0.08em] uppercase text-primary border border-primary/20 bg-primary/6 rounded-full px-3.5 py-1 mb-7">
          Estamos em Versão Beta
        </span>

        <h1 className="text-[48px] md:text-[68px] font-extrabold tracking-[-0.03em] leading-[1.06] max-w-[820px]">
          O assistente com IA que trabalha por você
        </h1>

        <p className="mt-5 text-[17px] md:text-[19px] text-[#555] max-w-[560px] leading-[1.55]">
          Descreva o que você precisa e o Terminal Agent cuida do resto.
          Planejamento, tarefas e respostas inteligentes, no terminal e no browser.
        </p>

        <form
          onSubmit={handleSubmit}
          className="mt-9 flex items-center gap-2 w-full max-w-[520px] bg-white border border-[#d4d4d8] rounded-xl px-4 py-2.5 shadow-sm"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="O que você precisa fazer hoje?"
            className="flex-1 bg-transparent text-sm text-[#0a0a14] placeholder:text-[#9ca3af] outline-none"
          />
          <Button type="submit" size="sm" className="px-5 h-8 text-sm shrink-0">
            Começar
          </Button>
        </form>
        <p className="mt-3 text-xs text-[#9ca3af]">
          Grátis durante o beta · Sem cartão de crédito
        </p>

        {/* Product mock — browser frame com chat */}
        <div className="mt-14 w-full max-w-[900px] rounded-2xl overflow-hidden border border-[#e5e7eb] shadow-[0_20px_60px_-10px_rgba(0,0,0,0.15)]">
          {/* Barra de browser */}
          <div className="bg-[#f4f4f5] border-b border-[#e5e7eb] px-4 py-2.5 flex items-center gap-3">
            <div className="flex gap-1.5">
              <div className="w-3 h-3 rounded-full bg-[#f87171]" />
              <div className="w-3 h-3 rounded-full bg-[#fbbf24]" />
              <div className="w-3 h-3 rounded-full bg-[#4ade80]" />
            </div>
            <div className="flex-1 mx-4 bg-white border border-[#e5e7eb] rounded-md text-[11px] text-center text-[#9ca3af] py-[3px] px-3">
              terminal-agent.app/chat
            </div>
          </div>

          {/* Interface de chat */}
          <div className="bg-white flex" style={{ height: 380 }}>
            {/* Sidebar */}
            <div className="w-[200px] bg-[#fafafa] border-r border-[#f0f0f0] p-3 flex flex-col gap-1 shrink-0">
              <div className="text-[11px] font-semibold text-[#0a0a14] px-2 py-1.5">
                Terminal Agent
              </div>
              <button className="text-left text-[12px] text-primary font-medium bg-primary/8 rounded-lg px-3 py-2 border border-primary/15">
                + Nova conversa
              </button>
              <div className="mt-2 text-[10px] font-semibold text-[#9ca3af] uppercase tracking-wide px-2">
                Hoje
              </div>
              {["Resumo das tarefas", "Plano de estudos", "Organização da semana"].map((t, i) => (
                <button
                  key={i}
                  className={`text-left text-[12px] rounded-lg px-3 py-2 truncate transition-colors ${
                    i === 0
                      ? "bg-white border border-[#e5e7eb] text-[#0a0a14] font-medium"
                      : "text-[#6b7280] hover:bg-white"
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>

            {/* Área de mensagens */}
            <div className="flex-1 flex flex-col overflow-hidden">
              <div className="flex-1 p-5 flex flex-col gap-4 overflow-hidden">
                {/* Mensagem do agente */}
                <div className="flex gap-3 items-start">
                  <div className="w-7 h-7 rounded-full bg-primary flex items-center justify-center text-white text-xs font-bold shrink-0">
                    A
                  </div>
                  <div className="bg-[#f4f4f5] rounded-2xl rounded-tl-sm px-4 py-2.5 text-[13px] text-[#0a0a14] max-w-[320px]">
                    Olá! Como posso ajudar você hoje?
                  </div>
                </div>

                {/* Mensagem do usuário */}
                <div className="flex gap-3 items-start justify-end">
                  <div className="bg-primary text-white rounded-2xl rounded-tr-sm px-4 py-2.5 text-[13px] max-w-[320px]">
                    Crie um resumo das minhas tarefas de hoje
                  </div>
                </div>

                {/* Resposta do agente */}
                <div className="flex gap-3 items-start">
                  <div className="w-7 h-7 rounded-full bg-primary flex items-center justify-center text-white text-xs font-bold shrink-0">
                    A
                  </div>
                  <div className="bg-[#f4f4f5] rounded-2xl rounded-tl-sm px-4 py-3 text-[13px] text-[#0a0a14] max-w-[340px]">
                    <div className="font-semibold mb-1.5">Suas tarefas para hoje:</div>
                    <ul className="text-[12px] space-y-1 text-[#555]">
                      <li>• Revisar o relatório trimestral</li>
                      <li>• Reunião com o time às 15h</li>
                      <li>• Enviar proposta ao cliente</li>
                    </ul>
                  </div>
                </div>
              </div>

              {/* Input */}
              <div className="p-3 border-t border-[#f0f0f0]">
                <div className="flex items-center gap-2 bg-[#fafafa] border border-[#e5e7eb] rounded-xl px-4 py-2.5">
                  <span className="text-[13px] text-[#9ca3af] flex-1">
                    Digite uma mensagem...
                  </span>
                  <span className="text-primary font-medium text-base">↑</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── COMO FUNCIONA ───────────────────────── */}
      <section id="como-funciona" className="bg-[#f7f8fa] px-6 py-24 mt-10">
        <div className="mx-auto max-w-[1200px]">
          <div className="text-center mb-16">
            <h2 className="text-[34px] md:text-[44px] font-bold tracking-[-0.025em]">
              Como funciona
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {howItWorks.map((s) => (
              <div key={s.num} className="bg-white rounded-2xl border border-[#e5e7eb] p-8">
                <div className="w-9 h-9 rounded-lg bg-primary/10 text-primary font-bold text-sm flex items-center justify-center mb-5">
                  {s.num}
                </div>
                <h3 className="text-[16px] font-semibold mb-2">{s.title}</h3>
                <p className="text-[14px] text-[#6b7280] leading-[1.6]">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── POR QUE TERMINAL AGENT? ─────────────── */}
      <section id="por-que" className="bg-white px-6 py-24">
        <div className="mx-auto max-w-[1200px]">
          <div className="max-w-[600px] mb-14">
            <h2 className="text-[34px] md:text-[44px] font-bold tracking-[-0.025em] mb-4">
              Construa hábitos com confiança
            </h2>
            <p className="text-[16px] text-[#6b7280] leading-[1.6]">
              A IA organiza por você. Você controla quem usa, o que vê e como se conecta ao seu fluxo de trabalho.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {whyCards.map((c) => (
              <div key={c.title} className="rounded-2xl border border-[#e5e7eb] p-7 hover:shadow-md transition-shadow">
                <h3 className="text-[15px] font-semibold mb-2">{c.title}</h3>
                <p className="text-[14px] text-[#6b7280] leading-[1.6]">{c.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── FUNCIONALIDADES ─────────────────────── */}
      <section id="funcionalidades" className="bg-[#f7f8fa] px-6 py-24 border-t border-[#e5e7eb]">
        <div className="mx-auto max-w-[1200px]">
          <div className="text-center mb-14">
            <h2 className="text-[34px] md:text-[44px] font-bold tracking-[-0.025em] mb-4">
              Tudo que você precisa para começar
            </h2>
            <p className="text-[16px] text-[#6b7280] max-w-[480px] mx-auto leading-[1.6]">
              O Terminal Agent já vem com autenticação, banco de dados e segurança prontos.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-5">
            {features.map((f) => (
              <div key={f.title} className="bg-white rounded-2xl border border-[#e5e7eb] p-7 hover:shadow-sm transition-shadow">
                <h3 className="text-[15px] font-semibold mb-2">{f.title}</h3>
                <p className="text-[14px] text-[#6b7280] leading-[1.6]">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA FINAL ───────────────────────────── */}
      <section className="bg-[#0a0a14] text-white px-6 py-24">
        <div className="mx-auto max-w-[700px] text-center">
          <h2 className="text-[34px] md:text-[48px] font-bold tracking-[-0.025em] mb-5">
            Junte-se à versão beta
          </h2>
          <p className="text-[16px] text-white/60 max-w-[440px] mx-auto leading-[1.6] mb-10">
            Acesso gratuito durante o beta. Crie sua conta agora e comece a usar em minutos.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link href="/register">
              <Button
                size="lg"
                className="bg-white text-[#0a0a14] hover:bg-white/90 px-10 h-12 text-[15px] font-semibold w-full sm:w-auto"
              >
                Criar conta grátis
              </Button>
            </Link>
            <Link href="/login">
              <Button
                size="lg"
                variant="outline"
                className="border-white/20 text-white hover:bg-white/10 px-10 h-12 text-[15px] w-full sm:w-auto"
              >
                Já tenho conta
              </Button>
            </Link>
          </div>
          <p className="mt-6 text-xs text-white/35">
            Suporte técnico disponível · Sem custo por usuário
          </p>
        </div>
      </section>

      {/* ── FOOTER ──────────────────────────────── */}
      <footer className="bg-white border-t border-[#e5e7eb] px-6 py-14">
        <div className="mx-auto max-w-[1200px]">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-10">
            <div className="col-span-2 md:col-span-1">
              <div className="font-bold text-[16px] mb-3">Terminal Agent</div>
              <p className="text-[13px] text-[#6b7280] leading-[1.6] max-w-[180px]">
                O assistente com IA que trabalha por você.
              </p>
            </div>

            <div>
              <div className="text-[12px] font-semibold uppercase tracking-wide text-[#9ca3af] mb-3">
                Geral
              </div>
              <ul className="space-y-2">
                {["Início", "Como funciona", "Funcionalidades"].map((l) => (
                  <li key={l}>
                    <a href="#" className="text-[13px] text-[#555] hover:text-[#0a0a14] transition-colors">
                      {l}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <div className="text-[12px] font-semibold uppercase tracking-wide text-[#9ca3af] mb-3">
                Produto
              </div>
              <ul className="space-y-2">
                {["Chat Web", "CLI Terminal", "API"].map((l) => (
                  <li key={l}>
                    <a href="#" className="text-[13px] text-[#555] hover:text-[#0a0a14] transition-colors">
                      {l}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <div className="text-[12px] font-semibold uppercase tracking-wide text-[#9ca3af] mb-3">
                Recursos
              </div>
              <ul className="space-y-2">
                {["Documentação", "Contato", "Privacidade", "Termos"].map((l) => (
                  <li key={l}>
                    <a href="#" className="text-[13px] text-[#555] hover:text-[#0a0a14] transition-colors">
                      {l}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="border-t border-[#e5e7eb] pt-7 flex flex-col sm:flex-row items-center justify-between gap-3">
            <p className="text-[12px] text-[#9ca3af]">
              © {new Date().getFullYear()} Terminal Agent · Versão Beta
            </p>
            <div className="flex items-center gap-5">
              <a href="#" className="text-[12px] text-[#9ca3af] hover:text-[#555] transition-colors">
                Privacidade
              </a>
              <a href="#" className="text-[12px] text-[#9ca3af] hover:text-[#555] transition-colors">
                Termos de uso
              </a>
            </div>
          </div>
        </div>
      </footer>

    </div>
  );
}
