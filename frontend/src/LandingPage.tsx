import React, { useState, useEffect } from 'react';
import { Upload, FileText, Loader2, Search, Download, FileCheck, Moon, Sun } from 'lucide-react';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';


const LandingPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);

  const [isDark, setIsDark] = useState(() => {
    const saved = localStorage.getItem('theme');
    if (saved) return saved === 'dark';
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    const root = window.document.documentElement;
    if (isDark) {
      root.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      root.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [isDark]);

  const generatePDF = () => {
    if (!analysisResult) return;

    const doc = new jsPDF();

    doc.setFontSize(20);
    doc.setTextColor(37, 99, 235);
    doc.text("CpsLyse - Rapport d'Audit Juridique", 14, 20);

    doc.setFontSize(10);
    doc.setTextColor(100);
    doc.text(`Document analysé: ${analysisResult.fileName}`, 14, 30);
    doc.text(`Score de conformité: ${analysisResult.complianceScore}`, 14, 35);
    doc.text(`Date de l'audit: ${new Date().toLocaleDateString()}`, 14, 40);

    autoTable(doc, {
      startY: 50,
      head: [['Clause du CPS', 'Référence Décret', 'Statut']],
      body: analysisResult.details.map((item: any) => [
        item.clause,
        item.ref,
        item.status
      ]),
      headStyles: { fillColor: [30, 41, 59] },
      styles: { fontSize: 9, cellPadding: 5 },
      columnStyles: {
        0: { cellWidth: 120 },
      }
    });

    doc.save(`Audit_CpsLyse_${analysisResult.fileName.replace('.pdf', '')}.pdf`);
  };

  const [expandedArticle, setExpandedArticle] = useState<number | null>(null);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/audit/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const data = await response.json();

      setAnalysisResult({
        fileName: file.name,
        complianceScore: "En cours...", // To be implemented later with actual analysis
        specialCount: data.message.includes("articles extracted") ? parseInt(data.message.split(" ")[2]) : 0,
        details: data.articles || [] // Assuming backend returns 'articles' key with list
      });

    } catch (error) {
      console.error('Error uploading file:', error);
      alert("Erreur lors de l'envoi du fichier. Vérifiez que le backend tourne.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors duration-300">
      <header className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 px-8 py-4 flex justify-between items-center sticky top-0 z-50">
        <div className="flex items-center gap-2">
          <div className="bg-blue-600 p-2 rounded-lg text-white"><Search size={20} /></div>
          <h1 className="text-xl font-bold dark:text-white tracking-tight">CpsLyse</h1>
        </div>

        <button
          onClick={() => setIsDark(!isDark)}
          className="p-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-transparent dark:border-slate-700 hover:ring-2 ring-blue-500 transition-all"
        >
          {isDark ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </header>

      <main className="max-w-7xl mx-auto p-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
        <section className="lg:col-span-4 space-y-6">
          <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
            <h3 className="text-lg font-semibold mb-4">Importation CPS</h3>
            <div className="border-2 border-dashed border-slate-200 dark:border-slate-700 rounded-xl p-8 flex flex-col items-center bg-slate-50 dark:bg-slate-800/50 hover:border-blue-400 transition-colors relative cursor-pointer">
              <input type="file" className="absolute inset-0 opacity-0 cursor-pointer" onChange={(e) => e.target.files && setFile(e.target.files[0])} />
              <Upload className="text-slate-400 mb-2" size={30} />
              <p className="text-sm text-slate-500 text-center">{file ? file.name : "Sélectionner un fichier PDF"}</p>
            </div>
            <div className="mt-4">
              <button
                onClick={() => handleUpload()}
                disabled={!file || loading}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-xl disabled:opacity-50 transition-all shadow-lg shadow-blue-200 dark:shadow-none"
              >
                {loading ? <Loader2 className="animate-spin mx-auto" size={20} /> : "Analyser CPS"}
              </button>
            </div>
          </div>

          {analysisResult && (
            <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 animate-in fade-in slide-in-from-bottom-4">
              <div className="flex justify-between items-center mb-4">
                <h3 className="font-semibold">Résumé de l'Audit</h3>
                <button
                  onClick={generatePDF}
                  className="p-2 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-lg transition-colors"
                  title="Télécharger le PDF"
                >
                  <Download size={20} />
                </button>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-100 dark:border-green-800 rounded-lg">
                  <p className="text-xs text-green-600 dark:text-green-400 font-bold uppercase">Conformité</p>
                  <p className="text-xl font-black">{analysisResult.complianceScore}</p>
                </div>
                <div className="p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-100 dark:border-amber-800 rounded-lg">
                  <p className="text-xs text-amber-600 dark:text-amber-400 font-bold uppercase">Spécificités</p>
                  <p className="text-xl font-black">{analysisResult.specialCount}</p>
                </div>
              </div>
            </div>
          )}
        </section>

        <section className="lg:col-span-8">
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden min-h-[500px] flex flex-col">
            <div className="px-6 py-4 bg-slate-50 dark:bg-slate-800/50 border-b border-slate-100 dark:border-slate-800 flex items-center gap-2">
              <FileCheck size={18} className="text-blue-600" />
              <span className="font-bold text-sm">RÉSULTATS DÉTAILLÉS</span>
            </div>

            <div className="p-6 flex-1">
              {!analysisResult && !loading ? (
                <div className="h-full flex flex-col items-center justify-center text-slate-400 py-20">
                  <FileText size={48} className="mb-4 opacity-20" />
                  <p>En attente d'importation...</p>
                </div>
              ) : loading ? (
                <div className="h-full flex flex-col items-center justify-center py-20">
                  <Loader2 className="animate-spin mb-4 text-blue-600" size={40} />
                  <p className="text-slate-500 animate-pulse">Audit en cours...</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left">
                    <thead>
                      <tr className="text-[10px] text-slate-400 uppercase tracking-widest">
                        <th className="pb-4 w-24">Article</th>
                        <th className="pb-4">Contenu</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                      {analysisResult.details.map((item: any, i: number) => (
                        <React.Fragment key={i}>
                          <tr
                            className="group hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors cursor-pointer"
                            onClick={() => setExpandedArticle(expandedArticle === i ? null : i)}
                          >
                            <td className="py-4 pr-4 whitespace-nowrap align-top">
                              <span className="px-2 py-1 bg-slate-100 dark:bg-slate-800 rounded text-xs font-mono font-bold">
                                {item.article_number || "N/A"}
                              </span>
                            </td>
                            <td className="py-4 text-sm leading-relaxed text-slate-600 dark:text-slate-300">
                              <div className={expandedArticle === i ? "" : "line-clamp-3 text-ellipsis overflow-hidden"}>
                                {item.content}
                              </div>
                              {item.content && item.content.length > 200 && (
                                <button
                                  className="mt-2 text-xs font-bold text-blue-600 dark:text-blue-400 hover:underline"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setExpandedArticle(expandedArticle === i ? null : i);
                                  }}
                                >
                                  {expandedArticle === i ? "Voir moins" : "Voir plus"}
                                </button>
                              )}
                            </td>
                          </tr>
                        </React.Fragment>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
};

export default LandingPage;
