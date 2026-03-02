import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />

      {/* Hero */}
      <section className="flex-1 flex flex-col items-center justify-center px-6 py-16 sm:py-20 text-center">
        <p className="text-label text-primary mb-4">
          TRIZ 기반 AI 특허 아이디어 발굴
        </p>
        <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-[48px] font-extrabold bg-gradient-to-r from-primary to-purple-400 bg-clip-text text-transparent mb-6">
          아이디어를 특허로
        </h1>
        <p className="text-body-l text-text-secondary max-w-[560px] mb-8">
          40가지 발명 원리로 당신의 문제를 혁신적인 특허 아이디어로 전환합니다
        </p>
        <Link href="/generate">
          <Button variant="primary" size="lg">
            무료로 시작하기
          </Button>
        </Link>
      </section>

      {/* 3단계 플로우 */}
      <section className="px-6 py-16 border-t border-border">
        <div className="max-w-content mx-auto grid grid-cols-1 md:grid-cols-3 gap-12">
          <div className="flex flex-col items-center text-center">
            <div className="w-12 h-12 rounded-full bg-primary text-white flex items-center justify-center font-bold text-lg mb-4">
              1
            </div>
            <h3 className="text-h3 text-text-primary mb-2">문제 입력</h3>
            <p className="text-body-m text-text-secondary">
              해결하고 싶은 문제나 키워드를 입력하세요
            </p>
          </div>
          <div className="flex flex-col items-center text-center">
            <div className="w-12 h-12 rounded-full bg-primary text-white flex items-center justify-center font-bold text-lg mb-4">
              2
            </div>
            <h3 className="text-h3 text-text-primary mb-2">AI 분석</h3>
            <p className="text-body-m text-text-secondary">
              TRIZ 원리와 선행특허를 분석합니다
            </p>
          </div>
          <div className="flex flex-col items-center text-center">
            <div className="w-12 h-12 rounded-full bg-primary text-white flex items-center justify-center font-bold text-lg mb-4">
              3
            </div>
            <h3 className="text-h3 text-text-primary mb-2">특허 초안 생성</h3>
            <p className="text-body-m text-text-secondary">
              KIPO 형식의 특허 초안을 DOCX로 받아보세요
            </p>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
