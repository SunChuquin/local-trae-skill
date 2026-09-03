import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { useState, useEffect, useCallback } from 'react';
import './index.css';
import { cn } from './lib/utils';
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Input } from './components/ui/input';
import { Textarea } from './components/ui/textarea';
import { Progress } from './components/ui/progress';
import { BookOpen, FileText, Database, Settings, Bug, BarChart3, Plus, Trash2, Upload, File, Search, Play, MessageSquare, Send, Bot, User, X, Brain, Bookmark, Check, Eye } from 'lucide-react';
import { knowledgeBaseApi } from './services/knowledgeBase';
import { documentApi, UploadProgress } from './services/document';
import { vectorApi } from './services/vector';
import { skillApi } from './services/skill';
import { excelDocApi, ExcelUploadProgress } from './services/excelDoc';
import { chatApi } from './services/chat';
import { agentApi, KBSelectionResponse } from './services/agent';
import { agentTemplateApi } from './services/agentTemplate';
import api from './services/api';
import { KnowledgeBase } from './types/knowledge_base';
import { Document } from './types/document';
import { ExcelDocument, ChunkMode } from './types/excel_document';
import { ChatMessage, ChatConfig, StreamChatEvent } from './types/chat';
import { useChat } from './hooks/useChat';
import { memoryApi, MemoryRecord } from './services/memory';
import { cleanPreviewApi, CleanPreviewItem } from './services/cleanPreview';

function Dashboard() {
  const [stats, setStats] = useState({ kbCount: 0, docCount: 0, vectorCount: 0 });

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const [kbs, health] = await Promise.all([
        knowledgeBaseApi.list(),
        api.get('/system/health').catch(() => ({ data: null })),
      ]);

      const kbsArray = Array.isArray(kbs) ? kbs : [];
      const healthData = (health as any)?.data;
      setStats({
        kbCount: kbsArray.length,
        docCount: healthData?.total_documents ?? kbsArray.reduce((sum, kb) => sum + (kb.document_count || 0), 0),
        vectorCount: healthData?.total_vectors ?? kbsArray.reduce((sum, kb) => sum + (kb.vector_count || 0), 0),
      });
    } catch (error) {
      console.error('Failed to load stats:', error);
      setStats({
        kbCount: 0,
        docCount: 0,
        vectorCount: 0,
      });
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">仪表盘</h1>
        <p className="text-muted-foreground">系统概览和管理中心</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">知识库数量</CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.kbCount}</div>
            <p className="text-xs text-muted-foreground">已创建的知识库</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">文档总数</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.docCount}</div>
            <p className="text-xs text-muted-foreground">已上传的文档</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">向量数量</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.vectorCount}</div>
            <p className="text-xs text-muted-foreground">已索引的向量</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">系统状态</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">健康</div>
            <p className="text-xs text-muted-foreground">系统运行正常</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>快速开始</CardTitle>
          <CardDescription>创建你的第一个知识库并开始管理文档</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Link to="/knowledge-bases">
              <div className="p-6 border rounded-lg hover:bg-accent transition-colors cursor-pointer">
                <BookOpen className="h-8 w-8 mb-2" />
                <h3 className="font-semibold mb-1">管理知识库</h3>
                <p className="text-sm text-muted-foreground">创建、编辑、删除知识库</p>
              </div>
            </Link>

            <Link to="/documents">
              <div className="p-6 border rounded-lg hover:bg-accent transition-colors cursor-pointer">
                <FileText className="h-8 w-8 mb-2" />
                <h3 className="font-semibold mb-1">管理文档</h3>
                <p className="text-sm text-muted-foreground">上传、编辑、删除文档</p>
              </div>
            </Link>

            <Link to="/vector">
              <div className="p-6 border rounded-lg hover:bg-accent transition-colors cursor-pointer">
                <Database className="h-8 w-8 mb-2" />
                <h3 className="font-semibold mb-1">向量管理</h3>
                <p className="text-sm text-muted-foreground">重建索引、备份还原</p>
              </div>
            </Link>

            <Link to="/skill">
              <div className="p-6 border rounded-lg hover:bg-accent transition-colors cursor-pointer">
                <Settings className="h-8 w-8 mb-2" />
                <h3 className="font-semibold mb-1">Skill 配置</h3>
                <p className="text-sm text-muted-foreground">配置检索参数</p>
              </div>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function KnowledgeBases() {
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newKbName, setNewKbName] = useState('');
  const [newKbDescription, setNewKbDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [generatingSummary, setGeneratingSummary] = useState<string | null>(null);
  const [showSummaryModal, setShowSummaryModal] = useState(false);
  const [selectedKbSummary, setSelectedKbSummary] = useState<any>(null);

  useEffect(() => {
    loadKnowledgeBases();
  }, []);

  const loadKnowledgeBases = async () => {
    try {
      const data = await knowledgeBaseApi.list();
      setKnowledgeBases(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Failed to load knowledge bases:', error);
      setKnowledgeBases([]);
    }
  };

  const handleCreate = async () => {
    if (!newKbName.trim()) return;

    setLoading(true);
    try {
      await knowledgeBaseApi.create({
        name: newKbName,
        description: newKbDescription
      });
      setShowCreateModal(false);
      setNewKbName('');
      setNewKbDescription('');
      await loadKnowledgeBases();
    } catch (error) {
      console.error('Failed to create knowledge base:', error);
      alert('创建知识库失败: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('确定要删除这个知识库吗？')) return;

    try {
      await knowledgeBaseApi.delete(id);
      await loadKnowledgeBases();
    } catch (error) {
      console.error('Failed to delete knowledge base:', error);
      alert('删除失败: ' + (error as Error).message);
    }
  };

  const handleGenerateSummary = async (kbId: string) => {
    setGeneratingSummary(kbId);
    try {
      await knowledgeBaseApi.generateSummary(kbId);
      alert('摘要生成成功！');
      await loadKnowledgeBases();
    } catch (error: any) {
      console.error('Failed to generate summary:', error);
      alert('摘要生成失败: ' + (error?.response?.data?.detail || error?.message || '未知错误'));
    } finally {
      setGeneratingSummary(null);
    }
  };

  const handleViewSummary = async (kb: KnowledgeBase) => {
    try {
      const summary = await knowledgeBaseApi.getSummary(kb.id);
      setSelectedKbSummary({
        ...summary,
        name: kb.name,
        document_count: kb.document_count
      });
      setShowSummaryModal(true);
    } catch (error) {
      console.error('Failed to get summary:', error);
      alert('获取摘要失败');
    }
  };

  const handleRegenerateAll = async () => {
    if (!confirm('确定要重新生成所有知识库的摘要吗？这可能需要一些时间。')) return;
    
    setLoading(true);
    try {
      const result = await knowledgeBaseApi.regenerateAllSummaries();
      alert(`批量生成完成！成功: ${result.success}, 失败: ${result.failed}`);
      await loadKnowledgeBases();
    } catch (error: any) {
      console.error('Failed to regenerate all summaries:', error);
      alert('批量生成失败: ' + (error?.response?.data?.detail || error?.message || '未知错误'));
    } finally {
      setLoading(false);
    }
  };

  const kbs = Array.isArray(knowledgeBases) ? knowledgeBases : [];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">知识库管理</h1>
          <p className="text-muted-foreground">创建和管理知识库</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleRegenerateAll} disabled={loading || kbs.length === 0}>
            批量生成摘要
          </Button>
          <Button onClick={() => setShowCreateModal(true)}>
            <Plus className="mr-2 h-4 w-4" />
            创建知识库
          </Button>
        </div>
      </div>

      {kbs.length === 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>知识库列表</CardTitle>
            <CardDescription>当前还没有创建任何知识库</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              点击上方按钮创建第一个知识库
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {kbs.map((kb) => (
            <Card key={kb.id}>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <CardTitle>{kb.name}</CardTitle>
                      {kb.summary && (
                        <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                          已生成摘要
                        </span>
                      )}
                      {!kb.summary && kb.document_count > 0 && (
                        <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-1 rounded">
                          暂无摘要
                        </span>
                      )}
                    </div>
                    <CardDescription>{kb.description || '暂无描述'}</CardDescription>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={() => handleViewSummary(kb)}>
                      查看摘要
                    </Button>
                    <Button 
                      variant="secondary" 
                      size="sm" 
                      onClick={() => handleGenerateSummary(kb.id)}
                      disabled={generatingSummary === kb.id}
                    >
                      {generatingSummary === kb.id ? '生成中...' : '生成摘要'}
                    </Button>
                    <Button variant="destructive" size="sm" onClick={() => handleDelete(kb.id)}>
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-sm text-muted-foreground">
                  <p>文档数量: {kb.document_count}</p>
                  <p>向量数量: {kb.vector_count}</p>
                  <p>创建时间: {new Date(kb.created_at).toLocaleString()}</p>
                  {kb.summary_updated_at && (
                    <p>摘要更新时间: {new Date(kb.summary_updated_at).toLocaleString()}</p>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>创建知识库</CardTitle>
              <CardDescription>输入知识库的名称和描述</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">名称</label>
                <Input
                  value={newKbName}
                  onChange={(e) => setNewKbName(e.target.value)}
                  placeholder="输入知识库名称"
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">描述</label>
                <Input
                  value={newKbDescription}
                  onChange={(e) => setNewKbDescription(e.target.value)}
                  placeholder="输入知识库描述（可选）"
                />
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setShowCreateModal(false)}>
                  取消
                </Button>
                <Button onClick={handleCreate} disabled={loading || !newKbName.trim()}>
                  {loading ? '创建中...' : '创建'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {showSummaryModal && selectedKbSummary && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>{selectedKbSummary.name} - 知识库摘要</CardTitle>
                  <CardDescription>
                    文档数量: {selectedKbSummary.document_count} | 
                    {selectedKbSummary.summary_updated_at 
                      ? ` 更新时间: ${new Date(selectedKbSummary.summary_updated_at).toLocaleString()}`
                      : ' 尚未生成摘要'
                    }
                  </CardDescription>
                </div>
                <Button variant="ghost" size="sm" onClick={() => setShowSummaryModal(false)}>
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {selectedKbSummary.has_summary ? (
                <>
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h4 className="font-medium text-blue-900 mb-2">摘要内容：</h4>
                    <p className="text-blue-800 text-sm whitespace-pre-wrap">
                      {selectedKbSummary.summary}
                    </p>
                  </div>
                  
                  <div className="flex justify-end gap-2 pt-4 border-t">
                    <Button 
                      variant="secondary"
                      onClick={() => {
                        setShowSummaryModal(false);
                        const kb = knowledgeBases.find(k => k.id === selectedKbSummary.kb_id);
                        if (kb) handleGenerateSummary(kb.id);
                      }}
                    >
                      重新生成摘要
                    </Button>
                  </div>
                </>
              ) : (
                <div className="text-center py-8">
                  <p className="text-muted-foreground mb-4">
                    该知识库还没有生成摘要
                  </p>
                  <Button onClick={() => {
                    setShowSummaryModal(false);
                    const kb = knowledgeBases.find(k => k.id === selectedKbSummary.kb_id);
                    if (kb) handleGenerateSummary(kb.id);
                  }}>
                    生成摘要
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

function Documents() {
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [selectedKb, setSelectedKb] = useState<string>('');
  const [documents, setDocuments] = useState<Document[]>([]);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newDocName, setNewDocName] = useState('');
  const [newDocContent, setNewDocContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<UploadProgress>({ phase: 'done', percent: 0, message: '' });
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 5;
  const [showVectorModal, setShowVectorModal] = useState(false);
  const [uploadingFiles, setUploadingFiles] = useState<File[]>([]);
  const [uploadedCount, setUploadedCount] = useState(0);
  const [failedCount, setFailedCount] = useState(0);
  const [failedFiles, setFailedFiles] = useState<string[]>([]);
  const [selectedDocumentVectors, setSelectedDocumentVectors] = useState<any>(null);
  const [loadingVectors, setLoadingVectors] = useState(false);

  useEffect(() => {
    loadKnowledgeBases();
  }, []);

  useEffect(() => {
    if (selectedKb) {
      loadDocuments();
    }
  }, [selectedKb]);

  const loadKnowledgeBases = async () => {
    try {
      const data = await knowledgeBaseApi.list();
      const kbsArray = Array.isArray(data) ? data : [];
      setKnowledgeBases(kbsArray);
      if (kbsArray.length > 0 && !selectedKb) {
        setSelectedKb(kbsArray[0].id);
      }
    } catch (error) {
      console.error('Failed to load knowledge bases:', error);
      setKnowledgeBases([]);
    }
  };

  const loadDocuments = async () => {
    if (!selectedKb) return;
    try {
      const data = await documentApi.list(selectedKb);
      setDocuments(data);
      setCurrentPage(1);
    } catch (error) {
      console.error('Failed to load documents:', error);
    }
  };

  const handleUpload = async (files: FileList | File[]) => {
    if (!selectedKb) {
      alert('请先选择知识库');
      return;
    }
    
    let fileArray = Array.from(files);
    if (fileArray.length === 0) return;
    
    // 过滤已完整上传的同名文件，防止重复向量化（vector_count >= chunk_count > 0 视为已完整上传）
    const existingNames = new Set<string>();
    try {
      const existing = await documentApi.list(selectedKb);
      existing.forEach((d) => {
        if (d.vector_count >= d.chunk_count && d.chunk_count > 0) {
          existingNames.add(d.name);
        }
      });
      const alreadyUploaded = fileArray.filter((f) => existingNames.has(f.name));
      fileArray = fileArray.filter((f) => !existingNames.has(f.name));
      if (alreadyUploaded.length > 0) {
        setUploadProgress({
          phase: 'upload',
          percent: 0,
          message: `已跳过 ${alreadyUploaded.length} 个已上传文件：${alreadyUploaded.map((f) => f.name).join('、')}`,
        });
      }
    } catch (error) {
      console.error('获取已入库文档失败，本次上传不做去重:', error);
    }
    
    if (fileArray.length === 0) {
      alert('所选文件均已完整上传，无需重复上传。');
      return;
    }
    
    setLoading(true);
    setUploadingFiles(fileArray);
    setUploadedCount(0);
    setFailedCount(0);
    setFailedFiles([]);
    setUploadProgress({ phase: 'upload', percent: 0, message: `准备上传 0/${fileArray.length}...` });
    
    let successCount = 0;
    let failCount = 0;
    
    for (let i = 0; i < fileArray.length; i++) {
      const file = fileArray[i];
      setUploadProgress({ 
        phase: 'upload', 
        percent: Math.round((i / fileArray.length) * 100), 
        message: `正在上传 ${i + 1}/${fileArray.length}: ${file.name}` 
      });
      
      try {
        await documentApi.upload(selectedKb, file, (progress) => {
          const globalPercent = Math.round((i + (progress.percent / 100)) / fileArray.length * 100);
          let message = `[${i + 1}/${fileArray.length}] ${progress.message}`;
          if (progress.estimateSeconds && progress.estimateSeconds > 1) {
            const mins = Math.ceil(progress.estimateSeconds / 60);
            message += mins >= 1 ? `（预计还需约 ${mins} 分钟）` : `（预计还需约 ${progress.estimateSeconds} 秒）`;
          }
          setUploadProgress({
            phase: progress.phase === 'done' ? 'done' : progress.phase,
            percent: globalPercent,
            message,
          });
        });
        successCount++;
      } catch (error) {
        console.error(`Failed to upload ${file.name}:`, error);
        failCount++;
        setFailedFiles((prev) => [...prev, file.name]);
      }
      
      setUploadedCount(successCount);
      setFailedCount(failCount);
    }
    
    setUploadProgress({ 
      phase: 'done', 
      percent: 100, 
      message: `完成！成功 ${successCount}，失败 ${failCount}` 
    });
    
    try {
      await loadDocuments();
    } catch (e) {
      console.error('Failed to reload documents:', e);
    }
    
    setLoading(false);
    
    if (failCount === 0) {
      alert(`成功上传 ${successCount} 个文档！`);
      setShowUploadModal(false);
    } else {
      alert(`上传完成：成功 ${successCount}，失败 ${failCount}`);
      if (successCount > 0) {
        setShowUploadModal(false);
      }
    }
    
    // 重置状态
    setTimeout(() => {
      setUploadProgress({ phase: 'done', percent: 0, message: '' });
      setUploadingFiles([]);
      setUploadedCount(0);
      setFailedCount(0);
      setFailedFiles([]);
    }, 2000);
  };

  const handleCreate = async () => {
    if (!selectedKb || !newDocName.trim()) return;

    setLoading(true);
    try {
      await documentApi.create({
        knowledge_base_id: selectedKb,
        name: newDocName,
        content: newDocContent,
        document_type: 'md'
      });
      setShowCreateModal(false);
      setNewDocName('');
      setNewDocContent('');
      await loadDocuments();
    } catch (error) {
      console.error('Failed to create document:', error);
      alert('创建失败: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (docId: string) => {
    if (!confirm('确定要删除这个文档吗？')) return;

    try {
      await documentApi.delete(docId);
      await loadDocuments();
    } catch (error) {
      console.error('Failed to delete document:', error);
      alert('删除失败: ' + (error as Error).message);
    }
  };

  const handleViewVectors = async (doc: Document) => {
    if (!selectedKb) return;

    setLoadingVectors(true);
    setShowVectorModal(true);
    setSelectedDocumentVectors(null);
    try {
      const result = await vectorApi.getDocumentVectors(selectedKb, doc.id);
      console.log('向量数据响应:', result);
      
      const vectorData = {
        ...result,
        document_name: doc.name
      };
      console.log('设置到状态的数据:', vectorData);
      setSelectedDocumentVectors(vectorData);
    } catch (error) {
      console.error('Failed to load vectors:', error);
      alert('加载向量数据失败: ' + (error as Error).message);
      setShowVectorModal(false);
    } finally {
      setLoadingVectors(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">文档管理</h1>
          <p className="text-muted-foreground">上传和管理文档</p>
        </div>
        <div className="flex gap-2">
          <select
            value={selectedKb}
            onChange={(e) => setSelectedKb(e.target.value)}
            className="border rounded px-3 py-2"
          >
            <option value="">选择知识库</option>
            {knowledgeBases.map((kb) => (
              <option key={kb.id} value={kb.id}>{kb.name}</option>
            ))}
          </select>
          <Button onClick={() => setShowUploadModal(true)} disabled={!selectedKb}>
            <Upload className="mr-2 h-4 w-4" />
            上传文档
          </Button>
          <Button onClick={() => setShowCreateModal(true)} disabled={!selectedKb}>
            <Plus className="mr-2 h-4 w-4" />
            新建文档
          </Button>
        </div>
      </div>

      {!selectedKb ? (
        <Card>
          <CardHeader>
            <CardTitle>文档列表</CardTitle>
            <CardDescription>请先选择知识库</CardDescription>
          </CardHeader>
        </Card>
      ) : documents.length === 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>文档列表</CardTitle>
            <CardDescription>当前知识库中没有文档</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              点击上方按钮上传或创建文档
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          <div className="grid gap-4">
            {documents
              .slice((currentPage - 1) * pageSize, currentPage * pageSize)
              .map((doc) => (
            <Card key={doc.id}>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div className="flex items-center gap-2">
                    <File className="h-5 w-5" />
                    <CardTitle className="text-lg">{doc.name}</CardTitle>
                    <span className="text-xs bg-gray-200 px-2 py-1 rounded">
                      {doc.document_type}
                    </span>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={() => handleViewVectors(doc)}>
                      <Database className="h-4 w-4 mr-1" />
                      查看向量
                    </Button>
                    <Button variant="destructive" size="sm" onClick={() => handleDelete(doc.id)}>
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-sm text-muted-foreground space-y-1">
                  <p>文件大小: {(doc.size / 1024).toFixed(2)} KB</p>
                  <p>分块数量: {doc.chunk_count}</p>
                  <p>向量数量: {doc.vector_count}</p>
                  <p>创建时间: {new Date(doc.created_at).toLocaleString()}</p>
                  {doc.content && (
                    <p className="mt-2 text-gray-600 line-clamp-3">
                      预览: {doc.content.substring(0, 200)}...
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
          </div>

          {Math.ceil(documents.length / pageSize) > 1 && (
            <div className="flex items-center justify-center gap-2 pt-2">
              <Button
                variant="outline"
                size="sm"
                disabled={currentPage <= 1}
                onClick={() => setCurrentPage((p) => p - 1)}
              >
                上一页
              </Button>
              <span className="text-sm text-muted-foreground px-3">
                第 {currentPage} / {Math.ceil(documents.length / pageSize)} 页
                （共 {documents.length} 条）
              </span>
              <Button
                variant="outline"
                size="sm"
                disabled={currentPage >= Math.ceil(documents.length / pageSize)}
                onClick={() => setCurrentPage((p) => p + 1)}
              >
                下一页
              </Button>
            </div>
          )}
        </div>
      )}

      {showUploadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>上传文档</CardTitle>
              <CardDescription>支持 MD、TXT、PDF、DOCX 格式，可一次选择多个文件</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <input
                type="file"
                accept=".md,.txt,.pdf,.docx"
                multiple
                onChange={(e) => {
                  const files = e.target.files;
                  if (files && files.length > 0) handleUpload(files);
                }}
                disabled={loading}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />

              {loading && (
                <div className="space-y-3">
                  <div className="flex justify-between items-center text-sm">
                    <span className={cn(
                      "font-medium",
                      uploadProgress.phase === 'upload' && "text-blue-600",
                      uploadProgress.phase === 'processing' && "text-orange-600",
                      uploadProgress.phase === 'done' && "text-emerald-600"
                    )}>
                      {uploadProgress.message}
                    </span>
                    <span className="text-muted-foreground">{uploadProgress.percent}%</span>
                  </div>
                  <Progress value={uploadProgress.percent} />
                  
                  {uploadingFiles.length > 1 && (
                    <>
                      <div className="flex justify-between text-xs">
                        <span className="text-emerald-600">成功: {uploadedCount}</span>
                        <span className="text-red-600">失败: {failedCount}</span>
                      </div>
                      {failedFiles.length > 0 && (
                        <div className="text-xs text-red-600 space-y-0.5">
                          <div className="font-medium">失败文件：</div>
                          {failedFiles.map((name) => (
                            <div key={name} className="truncate">• {name}</div>
                          ))}
                        </div>
                      )}
                    </>
                  )}
                </div>
              )}

              <div className="flex justify-end">
                <Button variant="outline" onClick={() => setShowUploadModal(false)} disabled={loading}>
                  关闭
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <CardHeader>
              <CardTitle>新建文档</CardTitle>
              <CardDescription>使用 Markdown 格式编写文档内容</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">文档名称</label>
                <Input
                  value={newDocName}
                  onChange={(e) => setNewDocName(e.target.value)}
                  placeholder="输入文档名称"
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">文档内容 (Markdown)</label>
                <Textarea
                  value={newDocContent}
                  onChange={(e) => setNewDocContent(e.target.value)}
                  placeholder="输入文档内容..."
                  className="min-h-[300px] font-mono"
                />
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setShowCreateModal(false)}>
                  取消
                </Button>
                <Button onClick={handleCreate} disabled={loading || !newDocName.trim()}>
                  {loading ? '创建中...' : '创建'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {showVectorModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            <div className="flex justify-between items-center p-6 border-b">
              <div>
                <h2 className="text-2xl font-bold">向量详情</h2>
                {selectedDocumentVectors && (
                  <p className="text-sm text-gray-600 mt-1">
                    文档: {selectedDocumentVectors.document_name} | 
                    知识库: {selectedDocumentVectors.knowledge_base_name} | 
                    向量数量: {selectedDocumentVectors.total}
                  </p>
                )}
              </div>
              <Button variant="ghost" size="sm" onClick={() => setShowVectorModal(false)}>
                <X className="h-5 w-5" />
              </Button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-6">
              {loadingVectors ? (
                <div className="flex items-center justify-center py-12">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
                    <p className="text-gray-600">正在加载向量数据...</p>
                  </div>
                </div>
              ) : selectedDocumentVectors && selectedDocumentVectors.vectors && selectedDocumentVectors.vectors.length > 0 ? (
                <div className="space-y-4">
                  {selectedDocumentVectors.vectors.map((vector: any, index: number) => (
                    <Card key={vector.id} className="border-l-4 border-l-blue-500">
                      <CardHeader>
                        <CardTitle className="text-sm flex justify-between items-center">
                          <span>向量 #{index + 1}</span>
                          <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                            维度: {vector.embedding_dimension}
                          </span>
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div>
                          <h4 className="text-sm font-medium text-gray-700 mb-1">Chunk ID:</h4>
                          <code className="text-xs bg-gray-100 p-2 rounded block break-all">{vector.id}</code>
                        </div>
                        <div>
                          <h4 className="text-sm font-medium text-gray-700 mb-1">内容:</h4>
                          <p className="text-sm bg-gray-50 p-3 rounded whitespace-pre-wrap max-h-40 overflow-y-auto">
                            {vector.content}
                          </p>
                        </div>
                        <div>
                          <h4 className="text-sm font-medium text-gray-700 mb-1">元数据:</h4>
                          <pre className="text-xs bg-gray-50 p-3 rounded overflow-x-auto">
                            {JSON.stringify(vector.metadata, null, 2)}
                          </pre>
                        </div>
                        {vector.embedding_preview && vector.embedding_preview.length > 0 && (
                          <div>
                            <h4 className="text-sm font-medium text-gray-700 mb-1">向量预览 (前10维):</h4>
                            <div className="flex flex-wrap gap-1">
                              {vector.embedding_preview.map((val: number, i: number) => (
                                <span key={i} className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded">
                                  {val.toFixed(4)}
                                </span>
                              ))}
                              <span className="text-xs text-gray-500 px-2 py-1">...</span>
                            </div>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <Database className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                  <p className="text-gray-500">
                    {selectedDocumentVectors ? '该文档暂无向量数据' : '未加载数据'}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function VectorManagement() {
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [selectedKb, setSelectedKb] = useState<string>('');
  const [testQuery, setTestQuery] = useState('');
  const [testResults, setTestResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [defaultTopK, setDefaultTopK] = useState<number>(5);

  useEffect(() => {
    loadKnowledgeBases();
    loadSkillConfig();

    const handleStorageChange = () => {
      loadSkillConfig();
    };
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const loadKnowledgeBases = async () => {
    try {
      const data = await knowledgeBaseApi.list();
      setKnowledgeBases(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Failed to load knowledge bases:', error);
      setKnowledgeBases([]);
    }
  };

  const loadSkillConfig = async () => {
    try {
      const config = await skillApi.getConfig();
      setDefaultTopK(config.top_k);
    } catch (error) {
      console.error('Failed to load skill config:', error);
    }
  };

  const handleTestRetrieval = async () => {
    if (!testQuery.trim()) return;

    setLoading(true);
    setHasSearched(true);
    
    console.log('========== 检索入参 ==========');
    console.log('查询语句:', testQuery);
    console.log('知识库:', undefined);
    console.log('top_k:', defaultTopK);
    console.log('================================');
    
    try {
      const results = await vectorApi.retrieve(testQuery, undefined, defaultTopK);
      console.log('检索原始返回:', results);
      console.log('检索结果数据:', results.data);
      setTestResults(results.data || []);
    } catch (error) {
      console.error('Failed to test retrieval:', error);
      alert('检索失败: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleRebuild = async () => {
    if (!selectedKb) return;

    if (!confirm('确定要重建向量索引吗？这将清除所有向量数据。')) return;

    setLoading(true);
    try {
      await vectorApi.rebuild(selectedKb);
      alert('重建成功');
    } catch (error) {
      console.error('Failed to rebuild vectors:', error);
      alert('重建失败: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">向量库管理</h1>
        <p className="text-muted-foreground">管理向量索引和备份</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>向量检索测试</CardTitle>
          <CardDescription>输入问题测试向量检索效果</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              value={testQuery}
              onChange={(e) => setTestQuery(e.target.value)}
              placeholder="输入问题进行检索测试..."
              onKeyPress={(e) => e.key === 'Enter' && handleTestRetrieval()}
            />
            <Button onClick={handleTestRetrieval} disabled={loading || !testQuery.trim()}>
              <Search className="mr-2 h-4 w-4" />
              检索
            </Button>
          </div>

          {testResults.length > 0 && (
            <div className="space-y-4 mt-4">
              <h4 className="font-semibold">检索结果 ({testResults.length})</h4>
              {testResults.map((result, index) => (
                <Card key={index}>
                  <CardContent className="pt-4">
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-medium">{result.document_name}</span>
                      <span className="text-sm text-green-600">
                        相似度: {(result.similarity * 100).toFixed(2)}%
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 line-clamp-3">
                      {result.content}
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {hasSearched && testResults.length === 0 && !loading && (
            <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-sm text-yellow-700">未找到相关文档，可能原因：</p>
              <ul className="text-sm text-yellow-600 mt-2 list-disc list-inside space-y-1">
                <li>知识库中还没有上传文档</li>
                <li>查询关键词与文档内容不匹配</li>
                <li>向量索引可能需要重建（点击下方"重建索引"按钮）</li>
              </ul>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>向量管理</CardTitle>
          <CardDescription>重建向量索引或备份数据</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <select
              value={selectedKb}
              onChange={(e) => setSelectedKb(e.target.value)}
              className="border rounded px-3 py-2 flex-1"
            >
              <option value="">选择知识库</option>
              {knowledgeBases.map((kb) => (
                <option key={kb.id} value={kb.id}>{kb.name}</option>
              ))}
            </select>
            <Button onClick={handleRebuild} disabled={!selectedKb || loading}>
              <Database className="mr-2 h-4 w-4" />
              重建索引
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function ExcelDocuments() {
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [selectedKb, setSelectedKb] = useState<string>('');
  const [excelDocs, setExcelDocs] = useState<ExcelDocument[]>([]);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showChunkModal, setShowChunkModal] = useState(false);
  const [currentDoc, setCurrentDoc] = useState<ExcelDocument | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<ExcelUploadProgress>({ phase: 'done', percent: 0, message: '' });
  const [chunkMode, setChunkMode] = useState<ChunkMode>('row_level');
  const [semanticThreshold, setSemanticThreshold] = useState<number>(0.7);
  const [includeHeaders, setIncludeHeaders] = useState<boolean>(true);
  const [chunkPreview, setChunkPreview] = useState<string[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 5;

  const loadKnowledgeBases = async () => {
    try {
      const data = await knowledgeBaseApi.list();
      const kbsArray = Array.isArray(data) ? data : [];
      setKnowledgeBases(kbsArray);
      if (kbsArray.length > 0 && !selectedKb) {
        setSelectedKb(kbsArray[0].id);
      }
    } catch (error) {
      console.error('Failed to load knowledge bases:', error);
      setKnowledgeBases([]);
    }
  };

  const loadExcelDocs = async () => {
    if (!selectedKb) return;
    try {
      const data = await excelDocApi.list(selectedKb);
      setExcelDocs(data);
      setCurrentPage(1);
    } catch (error) {
      console.error('Failed to load Excel documents:', error);
    }
  };

  useEffect(() => {
    loadKnowledgeBases();
  }, []);

  useEffect(() => {
    if (selectedKb) {
      loadExcelDocs();
    }
  }, [selectedKb]);

  const handleUpload = async (file: File) => {
    if (!selectedKb) {
      alert('请先选择知识库');
      return;
    }

    setLoading(true);
    setUploadProgress({ phase: 'upload', percent: 0, message: '准备上传...' });
    try {
      await excelDocApi.upload(selectedKb, file, (progress) => {
        setUploadProgress(progress);
      });
      await loadExcelDocs();
      setShowUploadModal(false);
      setUploadProgress({ phase: 'done', percent: 0, message: '' });
      alert('Excel 上传成功');
    } catch (error) {
      console.error('Failed to upload Excel:', error);
      alert('上传失败: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleChunkAndStore = async () => {
    if (!currentDoc) return;

    setLoading(true);
    setUploadProgress({ phase: 'processing', percent: 0, message: '准备分块...' });
    try {
      await excelDocApi.chunkAndStore(
        currentDoc.id,
        chunkMode,
        undefined,
        semanticThreshold,
        includeHeaders,
        (progress) => setUploadProgress(progress)
      );
      await loadExcelDocs();
      setShowChunkModal(false);
      setCurrentDoc(null);
      setUploadProgress({ phase: 'done', percent: 0, message: '' });
      alert('分块入库成功');
    } catch (error) {
      console.error('Failed to chunk and store:', error);
      alert('分块入库失败: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handlePreviewChunk = async () => {
    if (!currentDoc || !currentDoc.file_path) return;

    try {
      const preview = await excelDocApi.chunkPreview(
        currentDoc.file_path,
        chunkMode,
        undefined,
        semanticThreshold,
        includeHeaders
      );
      setChunkPreview(preview.map((p) => p.content));
    } catch (error) {
      console.error('Failed to preview chunk:', error);
    }
  };

  const handleDelete = async (docId: string) => {
    if (!confirm('确定要删除此 Excel 文档吗？')) return;
    try {
      await excelDocApi.delete(docId);
      await loadExcelDocs();
      alert('删除成功');
    } catch (error) {
      console.error('Failed to delete Excel document:', error);
      alert('删除失败');
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Excel 文档管理</h1>
        <p className="text-muted-foreground">上传和管理 Excel 文档</p>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium">知识库：</label>
          <select
            value={selectedKb}
            onChange={(e) => setSelectedKb(e.target.value)}
            className="border rounded px-3 py-2 text-sm"
          >
            <option value="">选择知识库</option>
            {knowledgeBases.map((kb) => (
              <option key={kb.id} value={kb.id}>
                {kb.name}
              </option>
            ))}
          </select>
        </div>
        <Button onClick={() => setShowUploadModal(true)} disabled={!selectedKb}>
          <Upload className="h-4 w-4 mr-2" />
          上传 Excel
        </Button>
      </div>

      {excelDocs.length === 0 ? (
        <Card>
          <CardContent className="py-8 text-center text-muted-foreground">
            {selectedKb ? '暂无 Excel 文档，请上传' : '请先选择知识库'}
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          <div className="grid gap-4">
            {excelDocs
              .slice((currentPage - 1) * pageSize, currentPage * pageSize)
              .map((doc) => (
            <Card key={doc.id}>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div className="flex items-center gap-2">
                    <File className="h-5 w-5" />
                    <CardTitle className="text-lg">{doc.name}</CardTitle>
                    <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                      Excel
                    </span>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setCurrentDoc(doc);
                        setShowChunkModal(true);
                      }}
                    >
                      配置分块
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => handleDelete(doc.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-sm text-muted-foreground space-y-1">
                  <p>文件大小: {(doc.size / 1024).toFixed(2)} KB</p>
                  <p>Sheet 数量: {doc.sheet_count}</p>
                  <div className="flex gap-4">
                    <span>分块数量: {doc.chunk_count}</span>
                    <span>向量数量: {doc.vector_count}</span>
                  </div>
                  <p>分块模式: {doc.chunk_mode === 'row_level' ? '行级分块' : '主题语义分块'}</p>
                  <p>创建时间: {new Date(doc.created_at).toLocaleString()}</p>
                </div>
              </CardContent>
            </Card>
            ))}
          </div>

          {Math.ceil(excelDocs.length / pageSize) > 1 && (
            <div className="flex items-center justify-center gap-2 pt-2">
              <Button
                variant="outline"
                size="sm"
                disabled={currentPage <= 1}
                onClick={() => setCurrentPage((p) => p - 1)}
              >
                上一页
              </Button>
              <span className="text-sm text-muted-foreground px-3">
                第 {currentPage} / {Math.ceil(excelDocs.length / pageSize)} 页
                （共 {excelDocs.length} 条）
              </span>
              <Button
                variant="outline"
                size="sm"
                disabled={currentPage >= Math.ceil(excelDocs.length / pageSize)}
                onClick={() => setCurrentPage((p) => p + 1)}
              >
                下一页
              </Button>
            </div>
          )}
        </div>
      )}

      {showUploadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>上传 Excel 文档</CardTitle>
              <CardDescription>支持 xlsx/xls 格式</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <input
                type="file"
                accept=".xlsx,.xls"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleUpload(file);
                }}
                disabled={loading}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100"
              />
              {loading && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className={cn(
                      "font-medium",
                      uploadProgress.phase === 'upload' && "text-blue-600",
                      uploadProgress.phase === 'processing' && "text-orange-600",
                      uploadProgress.phase === 'done' && "text-emerald-600"
                    )}>
                      {uploadProgress.message || (uploadProgress.phase === 'upload' ? '上传中...' : '处理中...')}
                    </span>
                    <span className="text-muted-foreground">{uploadProgress.percent}%</span>
                  </div>
                  <Progress value={uploadProgress.percent} />
                </div>
              )}
              <div className="flex justify-end">
                <Button variant="outline" onClick={() => {
                  setShowUploadModal(false);
                  setUploadProgress({ phase: 'done', percent: 0, message: '' });
                }}>
                  取消
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {showChunkModal && currentDoc && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-2xl max-h-[80vh] overflow-auto">
            <CardHeader>
              <CardTitle>配置分块 - {currentDoc.name}</CardTitle>
              <CardDescription>选择分块模式并预览效果</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">分块模式</label>
                  <select
                    value={chunkMode}
                    onChange={(e) => setChunkMode(e.target.value as ChunkMode)}
                    className="w-full border rounded px-3 py-2"
                  >
                    <option value="row_level">行级分块（结构化明细表）</option>
                    <option value="topic_semantic">主题语义分块（半结构化文档）</option>
                  </select>
                </div>
                {chunkMode === 'topic_semantic' && (
                  <div>
                    <label className="block text-sm font-medium mb-2">语义阈值: {semanticThreshold}</label>
                    <input
                      type="range"
                      min="0.3"
                      max="0.9"
                      step="0.1"
                      value={semanticThreshold}
                      onChange={(e) => setSemanticThreshold(parseFloat(e.target.value))}
                      className="w-full"
                    />
                  </div>
                )}
                <div className="col-span-2">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={includeHeaders}
                      onChange={(e) => setIncludeHeaders(e.target.checked)}
                    />
                    <span className="text-sm">包含表头上下文</span>
                  </label>
                </div>
              </div>

              <div className="flex gap-2">
                <Button onClick={handlePreviewChunk} variant="outline">
                  预览分块效果
                </Button>
              </div>

              {chunkPreview.length > 0 && (
                <div className="space-y-2 max-h-60 overflow-auto border rounded p-2">
                  <h4 className="text-sm font-medium">分块预览（前10条）：</h4>
                  {chunkPreview.map((content, idx) => (
                    <div key={idx} className="text-xs bg-gray-50 p-2 rounded">
                      <span className="font-medium">块 {idx + 1}: </span>
                      {content.substring(0, 200)}
                      {content.length > 200 && '...'}
                    </div>
                  ))}
                </div>
              )}

              {loading && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-orange-600 font-medium">{uploadProgress.message}</span>
                    <span className="text-muted-foreground">{uploadProgress.percent}%</span>
                  </div>
                  <Progress value={uploadProgress.percent} />
                </div>
              )}

              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => {
                  setShowChunkModal(false);
                  setCurrentDoc(null);
                  setChunkPreview([]);
                }}>
                  取消
                </Button>
                <Button onClick={handleChunkAndStore} disabled={loading}>
                  开始分块入库
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

function SkillConfig() {
  const [config, setConfig] = useState({
    description: '',
    top_k: 5,
    similarity_threshold: 0.5
  });
  const [metadata, setMetadata] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadConfig();
    loadMetadata();
  }, []);

  const loadConfig = async () => {
    try {
      const data = await skillApi.getConfig();
      setConfig({
        description: data.description,
        top_k: data.top_k,
        similarity_threshold: data.similarity_threshold
      });
    } catch (error) {
      console.error('Failed to load config:', error);
    }
  };

  const loadMetadata = async () => {
    try {
      const data = await skillApi.getMetadata();
      setMetadata(data);
    } catch (error) {
      console.error('Failed to load metadata:', error);
    }
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      await skillApi.updateConfig({
        description: config.description,
        top_k: config.top_k,
        similarity_threshold: config.similarity_threshold
      });
      localStorage.setItem('skill_config', JSON.stringify(config));
      alert('配置保存成功');
      await loadMetadata();
    } catch (error) {
      console.error('Failed to save config:', error);
      alert('保存失败: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Skill 配置</h1>
        <p className="text-muted-foreground">配置 Skill 描述和检索参数</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Function Calling 配置</CardTitle>
          <CardDescription>配置大模型调用时的参数</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium mb-2 block">Skill 描述</label>
            <Textarea
              value={config.description}
              onChange={(e) => setConfig({...config, description: e.target.value})}
              placeholder="输入 Skill 的描述，用于大模型判断何时调用"
              className="min-h-[100px]"
            />
            <p className="text-xs text-gray-500 mt-1">
              描述大模型的调用场景和使用限制
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Top K (返回结果数量)</label>
              <Input
                type="number"
                value={config.top_k}
                onChange={(e) => setConfig({...config, top_k: parseInt(e.target.value) || 5})}
                min={1}
                max={20}
              />
              <p className="text-xs text-gray-500 mt-1">
                1-20，默认为 5
              </p>
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">相似度阈值</label>
              <Input
                type="number"
                value={config.similarity_threshold}
                onChange={(e) => setConfig({...config, similarity_threshold: parseFloat(e.target.value) || 0.5})}
                min={0}
                max={1}
                step={0.1}
              />
              <p className="text-xs text-gray-500 mt-1">
                0-1，默认为 0.5
              </p>
            </div>
          </div>

          <div className="flex justify-end">
            <Button onClick={handleSave} disabled={loading}>
              {loading ? '保存中...' : '保存配置'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {metadata && (
        <Card>
          <CardHeader>
            <CardTitle>Function Calling JSON</CardTitle>
            <CardDescription>大模型使用的接口定义</CardDescription>
          </CardHeader>
          <CardContent>
            <pre className="bg-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
              {JSON.stringify(metadata.data, null, 2)}
            </pre>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

interface ChatProps {
  messages: ChatMessage[];
  setMessages: React.Dispatch<React.SetStateAction<ChatMessage[]>>;
  inputMessage: string;
  setInputMessage: React.Dispatch<React.SetStateAction<string>>;
  useSkill: boolean;
  setUseSkill: React.Dispatch<React.SetStateAction<boolean>>;
  isLoading: boolean;
  setIsLoading: React.Dispatch<React.SetStateAction<boolean>>;
  error: string;
  setError: React.Dispatch<React.SetStateAction<string>>;
  showConfig: boolean;
  setShowConfig: React.Dispatch<React.SetStateAction<boolean>>;
  config: ChatConfig;
  setConfig: React.Dispatch<React.SetStateAction<ChatConfig>>;
  showKBSelector: boolean;
  setShowKBSelector: React.Dispatch<React.SetStateAction<boolean>>;
  kbSelectionData: KBSelectionResponse | null;
  setKbSelectionData: React.Dispatch<React.SetStateAction<KBSelectionResponse | null>>;
  selectedKBs: string[];
  setSelectedKBs: React.Dispatch<React.SetStateAction<string[]>>;
  pendingQuery: string;
  setPendingQuery: React.Dispatch<React.SetStateAction<string>>;
  isSelectingKB: boolean;
  setIsSelectingKB: React.Dispatch<React.SetStateAction<boolean>>;
  messagesEndRef: React.RefObject<HTMLDivElement>;
  scrollToBottom: () => void;
  clearChat: () => void;
}

function Chat(props: ChatProps) {
  const {
    messages,
    setMessages,
    inputMessage,
    setInputMessage,
    useSkill,
    setUseSkill,
    isLoading,
    setIsLoading,
    error: _error,
    setError,
    showConfig,
    setShowConfig,
    config,
    setConfig,
    showKBSelector,
    setShowKBSelector,
    kbSelectionData,
    setKbSelectionData,
    selectedKBs,
    setSelectedKBs,
    pendingQuery,
    setPendingQuery,
    isSelectingKB,
    setIsSelectingKB,
    messagesEndRef,
    scrollToBottom,
    clearChat
  } = props;

  // 已保存到问答记忆的助手消息索引（用于按钮反馈）
  const [savedMemoryIndexes, setSavedMemoryIndexes] = useState<Set<number>>(new Set());

  useEffect(() => {
    loadConfig();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const loadConfig = async () => {
    try {
      const data = await chatApi.getConfig();
      setConfig(data);
    } catch (error) {
      console.error('Failed to load chat config:', error);
    }
  };

  const saveConfig = async () => {
    try {
      await chatApi.updateConfig(config.api_url, config.api_key, config.model);
      setShowConfig(false);
      alert('配置保存成功');
    } catch (error) {
      console.error('Failed to save config:', error);
      alert('配置保存失败');
    }
  };

  // 保存一条助手回答到问答记忆：取该回答之前最近的一条用户提问作为问题
  const handleSaveMemory = async (messageIndex: number, answer: string) => {
    const lastUserMessage = [...messages.slice(0, messageIndex)]
      .reverse()
      .find((m) => m.role === 'user');
    const question = lastUserMessage?.content?.trim();
    if (!question) {
      alert('未找到对应的问题，无法保存记忆');
      return;
    }
    try {
      const ok = await memoryApi.save(question, answer);
      if (ok) {
        setSavedMemoryIndexes((prev) => new Set(prev).add(messageIndex));
        alert('已保存到问答记忆');
      } else {
        alert('保存失败');
      }
    } catch (error) {
      console.error('保存问答记忆失败:', error);
      alert('保存失败');
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    if (!config.api_key) {
      setError('请先配置 LLM API Key');
      setShowConfig(true);
      return;
    }

    const userMessage: ChatMessage = { role: 'user', content: inputMessage };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInputMessage('');
    setError('');

    if (useSkill) {
      const currentQuery = inputMessage;
      setIsSelectingKB(true);
      setPendingQuery(currentQuery);
      
      setInputMessage('');
      
      try {
        const selectionResponse = await agentApi.selectKnowledgeBases({ query: currentQuery });
        
        console.log('KB Selection Response:', selectionResponse);
        
        if (!selectionResponse || typeof selectionResponse !== 'object') {
          throw new Error('知识库选择响应格式错误');
        }
        
        // 处理可能的响应格式：可能包含 data 字段，也可能直接是数据
        const selectionData: KBSelectionResponse = 'data' in selectionResponse ? selectionResponse.data as KBSelectionResponse : selectionResponse as KBSelectionResponse;
        
        setKbSelectionData(selectionData);
        
        // 调试：打印完整的推荐数据
        console.log('完整的推荐数据:', selectionData.recommendations);
        console.log('知识库列表:', selectionData.all_knowledge_bases);
        console.log('has_knowledge_bases:', selectionData.has_knowledge_bases);
        
        const recommendedKBs = (selectionData.recommendations || [])
          .map((r: any) => {
            console.log('单个推荐项:', r);
            console.log('knowledge_base:', r.knowledge_base);
            console.log('knowledge_base?.name:', r.knowledge_base?.name);
            return r.knowledge_base?.name;
          })
          .filter(Boolean);
        console.log('提取的推荐知识库:', recommendedKBs);
        
        setSelectedKBs(recommendedKBs);
        
        // 当KB Selection agent推荐知识库时，总是显示选择器询问用户
        // 即使recommendations为空，如果有知识库存在，也让用户选择
        if (selectionData.has_knowledge_bases) {
          setShowKBSelector(true);
        } else {
          // 没有知识库可用，直接使用通用模式
          await handleConfirmKBSelection(currentQuery);
        }
      } catch (error: any) {
        console.error('KB Selection error:', error);
        const errorMsg = error?.response?.data?.detail || error?.message || '知识库选择失败';
        
        setMessages(prev => {
          return [...prev, { 
            role: 'assistant', 
            content: `错误: ${errorMsg}` 
          }];
        });
      } finally {
        setIsSelectingKB(false);
      }
    } else {
      setIsLoading(true);
      try {
        // 创建初始助手消息（空内容）
        const initialAssistantMessage: ChatMessage = {
          role: 'assistant',
          content: '',
        };
        
        // 添加助手消息到消息列表
        const currentMessages = [...newMessages, initialAssistantMessage];
        setMessages(currentMessages);
        
        // 助手消息在数组中的索引
        const assistantIndex = currentMessages.length - 1;
        
        // 调用流式聊天API
        await chatApi.chatStream({
          messages: newMessages,
          use_skill: false,
        }, (event: StreamChatEvent) => {
          if (event.type === 'chunk' && event.content) {
            // 更新助手消息内容，追加新的chunk
            setMessages(prev => {
              const newMessages = [...prev];
              if (newMessages[assistantIndex]) {
                newMessages[assistantIndex] = {
                  ...newMessages[assistantIndex],
                  content: newMessages[assistantIndex].content + event.content
                };
              }
              return newMessages;
            });
          } else if (event.type === 'complete') {
            // 流式完成，可以记录日志
            console.log('流式响应完成，总长度:', event.content?.length || 0);
          } else if (event.type === 'error') {
            // 处理错误
            console.error('流式聊天错误:', event.error);
            setError(event.error || '流式聊天错误');
            
            // 更新助手消息为错误内容
            setMessages(prev => {
              const newMessages = [...prev];
              if (newMessages[assistantIndex]) {
                newMessages[assistantIndex] = {
                  ...newMessages[assistantIndex],
                  content: `错误: ${event.error || '未知错误'}`
                };
              }
              return newMessages;
            });
          }
        });
      } catch (error: any) {
        console.error('Chat error:', error);
        const errorMsg = error?.response?.data?.detail || error?.message || '发送消息失败';
        setError(errorMsg);
        
        // 更新助手消息为错误内容
        setMessages(prev => {
          const newMessages = [...prev];
          const assistantIndex = newMessages.length - 1;
          if (newMessages[assistantIndex] && newMessages[assistantIndex].role === 'assistant') {
            newMessages[assistantIndex] = {
              ...newMessages[assistantIndex],
              content: `错误: ${errorMsg}`
            };
          }
          return newMessages;
        });
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleConfirmKBSelection = async (queryParam?: string) => {
    setShowKBSelector(false);
    setIsLoading(true);
    
    let currentPendingQuery = queryParam || pendingQuery;
    
    // 防御性检查：如果查询为空，尝试从消息历史中获取最后一个用户消息
    if (!currentPendingQuery || currentPendingQuery.trim() === '') {
      const lastUserMessage = messages
        .filter(m => m.role === 'user')
        .slice(-1)[0];
      if (lastUserMessage && lastUserMessage.content) {
        currentPendingQuery = lastUserMessage.content;
        console.warn('警告：pendingQuery为空，使用最后一个用户消息内容:', currentPendingQuery);
      } else {
        console.error('错误：无法获取用户查询内容');
        setError('无法获取用户查询内容，请重新输入问题');
        setIsLoading(false);
        return;
      }
    }
    
    try {
      const userMessage: ChatMessage = { role: 'user', content: currentPendingQuery };
      
      // 检查用户消息是否已经在消息历史中
      const userMessageExists = messages.some(m => 
        m.role === 'user' && m.content === currentPendingQuery
      );
      
      

      
      // 构建发送给LLM的消息历史
      let messagesToSend: ChatMessage[];
      if (userMessageExists) {
        // 用户消息已存在，使用现有的messages（已经包含了用户消息）
        messagesToSend = [...messages];
      } else {
        // 用户消息不存在，添加用户消息到历史
        messagesToSend = [...messages, userMessage];
      }
      
      const hasSelectedKBs = selectedKBs.length > 0;
      
      console.log('========== 发送给 LLM 的消息 ==========');
      console.log('问题:', currentPendingQuery);
      console.log('use_skill:', hasSelectedKBs);
      console.log('knowledge_base_name:', hasSelectedKBs ? selectedKBs[0] : '无（通用模式）');
      console.log('messages:', JSON.stringify(messagesToSend, null, 2));
      console.log('=====================================');
      
      // 创建初始助手消息（空内容）
      const initialAssistantMessage: ChatMessage = {
        role: 'assistant',
        content: '',
      };
      
      // 根据用户消息是否存在，设置初始消息列表
      let currentMessages;
      if (userMessageExists) {
        // 用户消息已存在，只添加助手回复
        currentMessages = [...messages, initialAssistantMessage];
      } else {
        // 用户消息不存在，添加用户消息和助手回复
        currentMessages = [...messages, userMessage, initialAssistantMessage];
      }
      setMessages(currentMessages);
      
      // 助手消息在数组中的索引
      const assistantIndex = currentMessages.length - 1;
      
      // 调用流式聊天API
      await chatApi.chatStream({
        messages: messagesToSend,
        use_skill: hasSelectedKBs,
        knowledge_base_name: hasSelectedKBs ? selectedKBs[0] : undefined,
      }, (event: StreamChatEvent) => {
        if (event.type === 'chunk' && event.content) {
          // 更新助手消息内容，追加新的chunk
          setMessages(prev => {
            const newMessages = [...prev];
            if (newMessages[assistantIndex]) {
              newMessages[assistantIndex] = {
                ...newMessages[assistantIndex],
                content: newMessages[assistantIndex].content + event.content
              };
            }
            return newMessages;
          });
        } else if (event.type === 'complete') {
          // 流式完成，可以记录日志
          console.log('流式响应完成，总长度:', event.content?.length || 0);
        } else if (event.type === 'error') {
          // 处理错误
          console.error('流式聊天错误:', event.error);
          setError(event.error || '流式聊天错误');
          
          // 更新助手消息为错误内容
          setMessages(prev => {
            const newMessages = [...prev];
            if (newMessages[assistantIndex]) {
              newMessages[assistantIndex] = {
                ...newMessages[assistantIndex],
                content: `错误: ${event.error || '未知错误'}`
              };
            }
            return newMessages;
          });
        }
      });
    } catch (error: any) {
      console.error('Chat error:', error);
      const errorMsg = error?.response?.data?.detail || error?.message || '发送消息失败';
      setError(errorMsg);
      
      // 更新助手消息为错误内容
      setMessages(prev => {
        const newMessages = [...prev];
        const assistantIndex = newMessages.length - 1;
        if (newMessages[assistantIndex] && newMessages[assistantIndex].role === 'assistant') {
          newMessages[assistantIndex] = {
            ...newMessages[assistantIndex],
            content: `错误: ${errorMsg}`
          };
        }
        return newMessages;
      });
    } finally {
      setIsLoading(false);
      setPendingQuery('');
      setKbSelectionData(null);
      setSelectedKBs([]);
    }
  };

  const handleCancelKBSelection = () => {
    setShowKBSelector(false);
    setPendingQuery('');
    setKbSelectionData(null);
    setSelectedKBs([]);
  };

  const handleKBToggle = (kbName: string) => {
    setSelectedKBs(prev => 
      prev.includes(kbName)
        ? prev.filter(k => k !== kbName)
        : [...prev, kbName]
    );
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="space-y-6 h-[calc(100vh-180px)] flex flex-col">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">AI 对话</h1>
          <p className="text-muted-foreground">与 AI 对话，可选择是否使用私有文档 Skill</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => setShowConfig(true)}>
            <Settings className="h-4 w-4 mr-2" />
            LLM 配置
          </Button>
          <Button variant="outline" size="sm" onClick={clearChat}>
            <Trash2 className="h-4 w-4 mr-2" />
            清空对话
          </Button>
        </div>
      </div>

      <Card className="flex-1 flex flex-col overflow-hidden">
        <CardHeader className="flex-shrink-0 border-b">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={useSkill}
                  onChange={(e) => setUseSkill(e.target.checked)}
                  className="w-4 h-4"
                />
                <span className="text-sm font-medium">使用私有文档 Skill</span>
              </label>
              {useSkill && (
                <span className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded">
                  AI 将基于您的私有文档回答
                </span>
              )}
              {!useSkill && (
                <span className="text-xs text-gray-500 bg-gray-50 px-2 py-1 rounded">
                  使用通用模式回答
                </span>
              )}
            </div>
          </div>
        </CardHeader>

        <CardContent className="flex-1 overflow-auto p-4">
          <div className="space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-muted-foreground py-8">
                <Bot className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>开始对话吧！</p>
                <p className="text-sm mt-2">
                  {useSkill ? 'AI 将基于您的私有文档回答问题' : 'AI 将使用通用知识回答'}
                </p>
              </div>
            )}

            {messages.map((message, index) => (
              <div
                key={index}
                className={cn(
                  'flex gap-3',
                  message.role === 'user' && 'flex-row-reverse'
                )}
              >
                <div
                  className={cn(
                    'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
                    message.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-600'
                  )}
                >
                  {message.role === 'user' ? (
                    <User className="h-4 w-4" />
                  ) : (
                    <Bot className="h-4 w-4" />
                  )}
                </div>
                <div
                  className={cn(
                    'flex-1 rounded-lg p-3 max-w-[80%]',
                    message.role === 'user'
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-100'
                  )}
                >
                  <p className="whitespace-pre-wrap text-sm">{message.content}</p>
                  {message.role === 'assistant' && message.content && (
                    <button
                      onClick={() => handleSaveMemory(index, message.content)}
                      className="mt-2 inline-flex items-center gap-1 text-xs text-gray-400 hover:text-blue-600 transition-colors"
                    >
                      {savedMemoryIndexes.has(index) ? (
                        <Check className="h-3 w-3" />
                      ) : (
                        <Bookmark className="h-3 w-3" />
                      )}
                      {savedMemoryIndexes.has(index) ? '已记住' : '记住这次回答'}
                    </button>
                  )}
                </div>
              </div>
            ))}

            {isSelectingKB && (messages.length === 0 || messages[messages.length - 1].role !== 'assistant') && (
              <div className="flex gap-3">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center">
                  <Bot className="h-4 w-4" />
                </div>
                <div className="flex-1 bg-gray-100 rounded-lg p-3">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                  </div>
                </div>
              </div>
            )}

            {isLoading && (messages.length === 0 || messages[messages.length - 1].role !== 'assistant') && (
              <div className="flex gap-3">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center">
                  <Bot className="h-4 w-4" />
                </div>
                <div className="flex-1 bg-gray-100 rounded-lg p-3">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                  </div>
                </div>
              </div>
            )}

            {showKBSelector && kbSelectionData && (messages.length === 0 || messages[messages.length - 1].role !== 'assistant') && (
              <div className="flex gap-3">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-500 text-white flex items-center justify-center">
                  <Bot className="h-4 w-4" />
                </div>
                <div className="flex-1 bg-blue-50 border border-blue-200 rounded-lg p-4 max-w-[85%]">
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium text-blue-900 mb-2">🔍 知识库选择</h4>
                      {kbSelectionData.analysis && (
                        <p className="text-sm text-gray-700 mb-3">{kbSelectionData.analysis}</p>
                      )}
                    </div>
                    
                    {kbSelectionData.recommendations && kbSelectionData.recommendations.length > 0 && (
                      <div className="space-y-2">
                        <h5 className="text-sm font-medium text-gray-700">AI 推荐的知识库：</h5>
                        {kbSelectionData.recommendations.map((rec: any, idx: number) => (
                          <div key={idx} className="bg-white border rounded-lg p-3">
                            <div className="flex items-center gap-2 mb-1">
                              <input
                                type="checkbox"
                                checked={selectedKBs.includes(rec.knowledge_base.name)}
                                onChange={() => handleKBToggle(rec.knowledge_base.name)}
                                className="w-4 h-4"
                              />
                              <span className="font-medium text-sm">{rec.knowledge_base.name}</span>
                              <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded">
                                {(rec.confidence * 100).toFixed(0)}%
                              </span>
                            </div>
                            <p className="text-xs text-gray-600 ml-6">{rec.reason}</p>
                          </div>
                        ))}
                      </div>
                    )}
                    
                    {kbSelectionData.all_knowledge_bases && kbSelectionData.all_knowledge_bases.length > 0 && (
                      <div className="space-y-2">
                        <h5 className="text-sm font-medium text-gray-700">其他知识库：</h5>
                        {kbSelectionData.all_knowledge_bases
                          .filter((kb: any) => !selectedKBs.includes(kb.name))
                          .map((kb: any, idx: number) => (
                            <div key={idx} className="bg-white border rounded-lg p-3">
                              <div className="flex items-center gap-2 mb-1">
                                <input
                                  type="checkbox"
                                  checked={selectedKBs.includes(kb.name)}
                                  onChange={() => handleKBToggle(kb.name)}
                                  className="w-4 h-4"
                                />
                                <span className="font-medium text-sm">{kb.name}</span>
                                <span className="text-xs text-gray-500">
                                  ({kb.document_count} 个文档)
                                </span>
                              </div>
                              {kb.summary && (
                                <p className="text-xs text-gray-600 ml-6 line-clamp-2">{kb.summary}</p>
                              )}
                            </div>
                          ))}
                      </div>
                    )}
                    
                    <div className="flex justify-end gap-2 pt-3 border-t">
                      <Button variant="outline" size="sm" onClick={handleCancelKBSelection}>
                        取消
                      </Button>
                      <Button size="sm" onClick={() => handleConfirmKBSelection(pendingQuery)}>
                        确认并回答
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </CardContent>

        <div className="flex-shrink-0 border-t p-4">
          <div className="flex gap-2">
            <Textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder={useSkill ? '输入问题，AI 将基于私有文档回答...' : '输入问题...'}
              className="flex-1 min-h-[60px] max-h-[120px]"
              disabled={isLoading}
            />
            <Button
              onClick={handleSendMessage}
              disabled={isLoading || !inputMessage.trim()}
              className="self-end"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </Card>

      {showConfig && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle>LLM API 配置</CardTitle>
                <Button variant="ghost" size="sm" onClick={() => setShowConfig(false)}>
                  <X className="h-4 w-4" />
                </Button>
              </div>
              <CardDescription>配置大模型 API 以使用对话功能</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">API 地址</label>
                <Input
                  value={config.api_url}
                  onChange={(e) => setConfig({ ...config, api_url: e.target.value })}
                  placeholder="https://api.openai.com/v1/chat/completions"
                />
                <p className="text-xs text-gray-500 mt-1">支持 OpenAI 兼容格式的 API 地址</p>
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">API Key</label>
                <Input
                  type="password"
                  value={config.api_key}
                  onChange={(e) => setConfig({ ...config, api_key: e.target.value })}
                  placeholder="sk-..."
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">模型</label>
                <Input
                  value={config.model}
                  onChange={(e) => setConfig({ ...config, model: e.target.value })}
                  placeholder="gpt-4o-mini"
                />
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setShowConfig(false)}>
                  取消
                </Button>
                <Button onClick={saveConfig}>
                  保存配置
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

function MemoryManagement() {
  const [records, setRecords] = useState<MemoryRecord[]>([]);
  const [loading, setLoading] = useState(false);

  const loadMemories = useCallback(async () => {
    setLoading(true);
    try {
      const data = await memoryApi.list(200, 0);
      setRecords(data);
    } catch (error) {
      console.error('加载问答记忆失败:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadMemories();
  }, [loadMemories]);

  const handleDelete = async (id: string) => {
    if (!window.confirm('确定删除这条记忆吗？删除后不可恢复。')) return;
    try {
      const ok = await memoryApi.remove(id);
      if (ok) {
        setRecords((prev) => prev.filter((r) => r.id !== id));
      } else {
        alert('删除失败，记忆可能不存在');
      }
    } catch (error) {
      console.error('删除问答记忆失败:', error);
      alert('删除失败');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">问答记忆</h1>
          <p className="text-muted-foreground">
            管理已保存的问答记忆（共 {records.length} 条）
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={loadMemories}>
          刷新
        </Button>
      </div>

      {loading ? (
        <Card>
          <CardContent className="p-6 text-center text-muted-foreground">加载中...</CardContent>
        </Card>
      ) : records.length === 0 ? (
        <Card>
          <CardContent className="p-6 text-center text-muted-foreground">
            暂无记忆。可在「AI 对话」中对助手回答点击"记住这次回答"保存。
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {records.map((rec) => (
            <Card key={rec.id}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 space-y-2 min-w-0">
                    <div className="flex items-start gap-2">
                      <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded shrink-0 mt-0.5">
                        问题
                      </span>
                      <span className="font-medium text-sm break-words">{rec.question}</span>
                    </div>
                    <div className="flex items-start gap-2">
                      <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded shrink-0 mt-0.5">
                        回答
                      </span>
                      <p className="text-sm text-gray-700 whitespace-pre-wrap break-words line-clamp-4">
                        {rec.answer}
                      </p>
                    </div>
                    {rec.created_at && (
                      <p className="text-xs text-muted-foreground">
                        保存时间：{new Date(rec.created_at).toLocaleString()}
                      </p>
                    )}
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    className="shrink-0"
                    onClick={() => handleDelete(rec.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

function CleanPreviewPage() {
  const [items, setItems] = useState<CleanPreviewItem[]>([]);
  const [selectedName, setSelectedName] = useState<string | null>(null);
  const [original, setOriginal] = useState('');
  const [cleaned, setCleaned] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingContent, setLoadingContent] = useState(false);

  const loadList = useCallback(async () => {
    setLoading(true);
    try {
      const data = await cleanPreviewApi.list();
      setItems(data);
      if (data.length > 0) {
        setSelectedName((prev) => prev && data.some((d) => d.name === prev) ? prev : data[0].name);
      } else {
        setSelectedName(null);
        setOriginal('');
        setCleaned('');
      }
    } catch (error) {
      console.error('加载剔除预览列表失败:', error);
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadList();
  }, [loadList]);

  // 默认打开第一个
  useEffect(() => {
    if (!selectedName && items.length > 0) {
      setSelectedName(items[0].name);
    }
  }, [items, selectedName]);

  useEffect(() => {
    if (!selectedName) {
      setOriginal('');
      setCleaned('');
      return;
    }
    let cancelled = false;
    setLoadingContent(true);
    Promise.all([
      cleanPreviewApi.content(selectedName, 'original'),
      cleanPreviewApi.content(selectedName, 'cleaned'),
    ])
      .then(([o, c]) => {
        if (cancelled) return;
        setOriginal(o);
        setCleaned(c);
      })
      .catch((error) => {
        console.error('加载剔除预览内容失败:', error);
        if (!cancelled) {
          setOriginal('');
          setCleaned('');
        }
      })
      .finally(() => {
        if (!cancelled) setLoadingContent(false);
      });
    return () => {
      cancelled = true;
    };
  }, [selectedName]);

  const removedChars = original.length - cleaned.length;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">剔除预览</h1>
          <p className="text-muted-foreground">
            检查上传 PDF 的页眉/页脚剔除是否正确（共 {items.length} 个文件）
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={loadList}>
          刷新
        </Button>
      </div>

      {loading ? (
        <Card>
          <CardContent className="p-6 text-center text-muted-foreground">加载中...</CardContent>
        </Card>
      ) : items.length === 0 ? (
        <Card>
          <CardContent className="p-6 text-center text-muted-foreground">
            暂无剔除预览。请先上传 PDF 文档，系统会同时保存剔除前/后的文本供对比。
          </CardContent>
        </Card>
      ) : (
        <div className="flex gap-6 h-[calc(100vh-220px)] min-h-[480px]">
          {/* 左侧文件列表 */}
          <div className="w-64 shrink-0 border rounded-lg overflow-y-auto bg-card">
            {items.map((item) => (
              <button
                key={item.name}
                onClick={() => setSelectedName(item.name)}
                className={`w-full text-left px-3 py-2.5 text-sm border-b last:border-b-0 transition-colors ${
                  selectedName === item.name
                    ? 'bg-blue-50 text-blue-700 font-medium'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
                title={item.name}
              >
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4 shrink-0" />
                  <span className="truncate">{item.name}</span>
                </div>
              </button>
            ))}
          </div>

          {/* 右侧对比面板 */}
          <div className="flex-1 min-w-0 flex flex-col space-y-4">
            {selectedName && (
              <div className="flex items-center gap-3 text-sm text-muted-foreground">
                <span className="font-medium text-gray-800 truncate">{selectedName}</span>
                <span className="shrink-0">
                  剔除前 {original.length} 字 → 剔除后 {cleaned.length} 字
                </span>
                {removedChars > 0 ? (
                  <span className="shrink-0 text-emerald-600">已剔除 {removedChars} 字</span>
                ) : (
                  <span className="shrink-0 text-amber-600">未识别到页眉/页脚</span>
                )}
              </div>
            )}

            {loadingContent ? (
              <Card>
                <CardContent className="p-6 text-center text-muted-foreground">加载中...</CardContent>
              </Card>
            ) : (
              <div className="flex-1 min-h-0 grid grid-cols-2 gap-4">
                <div className="flex flex-col min-h-0">
                  <div className="text-xs font-medium text-muted-foreground mb-1">
                    剔除前（原始提取）
                  </div>
                  <pre className="flex-1 min-h-0 overflow-auto border rounded-lg p-3 text-xs leading-relaxed bg-card whitespace-pre-wrap break-words">
                    {original || '（空）'}
                  </pre>
                </div>
                <div className="flex flex-col min-h-0">
                  <div className="text-xs font-medium text-emerald-600 mb-1">
                    剔除后（页眉/页脚已去除）
                  </div>
                  <pre className="flex-1 min-h-0 overflow-auto border rounded-lg p-3 text-xs leading-relaxed bg-card whitespace-pre-wrap break-words">
                    {cleaned || '（空）'}
                  </pre>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function DebugPanel() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleTest = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError('');
    try {
      const data = await skillApi.test(query, undefined, 5);
      setResults(data.data?.results || []);
    } catch (error) {
      console.error('Failed to test skill:', error);
      setError('测试失败: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">调试面板</h1>
        <p className="text-muted-foreground">测试 Skill 调用效果</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>在线测试</CardTitle>
          <CardDescription>输入问题测试检索效果（模拟大模型调用）</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="输入问题..."
              onKeyPress={(e) => e.key === 'Enter' && handleTest()}
            />
            <Button onClick={handleTest} disabled={loading || !query.trim()}>
              <Play className="mr-2 h-4 w-4" />
              测试
            </Button>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {results.length > 0 && (
            <div className="space-y-4">
              <h4 className="font-semibold">测试结果 ({results.length})</h4>
              {results.map((result, index) => (
                <Card key={index}>
                  <CardContent className="pt-4">
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-medium">{result.document_name}</span>
                      <span className="text-sm text-green-600">
                        相似度: {(result.similarity * 100).toFixed(2)}%
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 whitespace-pre-wrap">
                      {result.content_preview || result.content}
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>调用日志</CardTitle>
          <CardDescription>查看最近的 API 调用记录</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            调用日志功能开发中...
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

function AgentTemplates() {
  const [agents, setAgents] = useState<any[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [expandedTemplates, setExpandedTemplates] = useState<Set<string>>(new Set());

  useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await agentTemplateApi.list();
      setAgents(data);
      if (data.length > 0) {
        setSelectedAgent(data[0]);
      }
    } catch (error) {
      console.error('Failed to load agents:', error);
      setError('加载智能体列表失败: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const toggleTemplate = (templateName: string) => {
    const newExpanded = new Set(expandedTemplates);
    if (newExpanded.has(templateName)) {
      newExpanded.delete(templateName);
    } else {
      newExpanded.add(templateName);
    }
    setExpandedTemplates(newExpanded);
  };

  const getAgentTypeName = (type: string) => {
    const typeMap: Record<string, string> = {
      selector: '选择器',
      assistant: '助手',
      analyzer: '分析器',
    };
    return typeMap[type] || type;
  };

  const getStatusColor = (status: string) => {
    return status === 'active' ? 'text-green-600' : 'text-gray-500';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-muted-foreground">加载中...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">智能体管理</h1>
          <p className="text-muted-foreground">管理和查看系统内置智能体</p>
        </div>
        <Card>
          <CardContent className="pt-6">
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">智能体管理</h1>
        <p className="text-muted-foreground">管理和查看系统内置智能体及提示词模板</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>智能体列表</CardTitle>
            <CardDescription>共 {agents.length} 个内置智能体</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {agents.map((agent) => (
              <div
                key={agent.id}
                onClick={() => setSelectedAgent(agent)}
                className={cn(
                  "p-4 border rounded-lg cursor-pointer transition-colors",
                  selectedAgent?.id === agent.id
                    ? "bg-blue-50 border-blue-300"
                    : "hover:bg-gray-50 border-gray-200"
                )}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-semibold text-sm">{agent.name}</h3>
                    <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                      {agent.description}
                    </p>
                    <div className="flex items-center gap-2 mt-2">
                      <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                        {getAgentTypeName(agent.type)}
                      </span>
                      <span className={cn("text-xs", getStatusColor(agent.status))}>
                        ● {agent.status === 'active' ? '活跃' : '已停用'}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="mt-2 text-xs text-muted-foreground">
                  模板数量: {agent.templates?.length || 0}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>{selectedAgent?.name || '选择智能体'}</CardTitle>
            <CardDescription>
              {selectedAgent?.description || '请从左侧选择一个智能体查看详情'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {selectedAgent ? (
              <div className="space-y-4">
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <span>类型: {getAgentTypeName(selectedAgent.type)}</span>
                  <span>状态: <span className={getStatusColor(selectedAgent.status)}>{selectedAgent.status === 'active' ? '活跃' : '已停用'}</span></span>
                  <span>创建时间: {new Date(selectedAgent.created_at).toLocaleString('zh-CN')}</span>
                </div>

                <div className="border-t pt-4">
                  <h4 className="font-semibold mb-3">提示词模板 ({selectedAgent.templates?.length || 0})</h4>
                  
                  {selectedAgent.templates && selectedAgent.templates.length > 0 ? (
                    <div className="space-y-4">
                      {selectedAgent.templates.map((template: any, index: number) => (
                        <div key={index} className="border rounded-lg overflow-hidden">
                          <div
                            onClick={() => toggleTemplate(template.name)}
                            className="bg-gray-50 px-4 py-3 cursor-pointer flex items-center justify-between hover:bg-gray-100 transition-colors"
                          >
                            <div>
                              <h5 className="font-medium text-sm">{template.name}</h5>
                              <p className="text-xs text-muted-foreground mt-1">
                                {template.description}
                              </p>
                            </div>
                            <div className="flex items-center gap-3">
                              <span className="text-xs text-muted-foreground">
                                v{template.version}
                              </span>
                              <span className="text-gray-400">
                                {expandedTemplates.has(template.name) ? '▲' : '▼'}
                              </span>
                            </div>
                          </div>

                          {expandedTemplates.has(template.name) && (
                            <div className="p-4 border-t bg-white">
                              <div className="mb-3">
                                <span className="text-sm font-medium">变量列表:</span>
                                <div className="flex flex-wrap gap-2 mt-2">
                                  {template.variables && template.variables.length > 0 ? (
                                    template.variables.map((variable: string, i: number) => (
                                      <span key={i} className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                                        {`{${variable}}`}
                                      </span>
                                    ))
                                  ) : (
                                    <span className="text-xs text-muted-foreground">无变量</span>
                                  )}
                                </div>
                              </div>

                              <div>
                                <span className="text-sm font-medium">模板内容:</span>
                                <pre className="mt-2 p-4 bg-gray-50 border rounded-lg text-xs overflow-x-auto whitespace-pre-wrap font-mono max-h-96 overflow-y-auto">
                                  {template.content}
                                </pre>
                              </div>

                              <div className="mt-3 text-xs text-muted-foreground">
                                最后更新: {new Date(template.last_updated).toLocaleString('zh-CN')}
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-sm text-muted-foreground">暂无提示词模板</div>
                  )}
                </div>
              </div>
            ) : (
              <div className="text-center text-muted-foreground py-8">
                请从左侧选择一个智能体查看详情
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function App() {
  const location = useLocation();
  const chatState = useChat();

  return (
    <div className="min-h-screen bg-background">
      <div className="flex">
        <aside className="w-64 border-r bg-card h-screen fixed left-0 top-0">
          <div className="p-6 border-b">
            <h2 className="text-xl font-bold">📚 私有文档 Skill</h2>
          </div>
          <nav className="p-4 space-y-2">
            <Link to="/">
              <Button
                variant={location.pathname === '/' ? 'secondary' : 'ghost'}
                className="w-full justify-start"
              >
                <BarChart3 className="mr-2 h-4 w-4" />
                仪表盘
              </Button>
            </Link>
            <Link to="/knowledge-bases">
              <Button
                variant={location.pathname === '/knowledge-bases' ? 'secondary' : 'ghost'}
                className="w-full justify-start"
              >
                <BookOpen className="mr-2 h-4 w-4" />
                知识库管理
              </Button>
            </Link>
            <Link to="/documents">
              <Button
                variant={location.pathname === '/documents' ? 'secondary' : 'ghost'}
                className="w-full justify-start"
              >
                <FileText className="mr-2 h-4 w-4" />
                文档管理
              </Button>
            </Link>
            <Link to="/clean-preview">
              <Button
                variant={location.pathname === '/clean-preview' ? 'secondary' : 'ghost'}
                className="w-full justify-start"
              >
                <Eye className="mr-2 h-4 w-4" />
                剔除预览
              </Button>
            </Link>
            <Link to="/memories">
              <Button
                variant={location.pathname === '/memories' ? 'secondary' : 'ghost'}
                className="w-full justify-start"
              >
                <Bookmark className="mr-2 h-4 w-4" />
                记忆管理
              </Button>
            </Link>
            <Link to="/chat">
              <Button
                variant={location.pathname === '/chat' ? 'secondary' : 'ghost'}
                className="w-full justify-start"
              >
                <MessageSquare className="mr-2 h-4 w-4" />
                AI 对话
              </Button>
            </Link>
            <Link to="/excel-documents">
              <Button
                variant={location.pathname === '/excel-documents' ? 'secondary' : 'ghost'}
                className="w-full justify-start"
              >
                <File className="mr-2 h-4 w-4" />
                Excel 文档
              </Button>
            </Link>
            <Link to="/vector">
              <Button
                variant={location.pathname === '/vector' ? 'secondary' : 'ghost'}
                className="w-full justify-start"
              >
                <Database className="mr-2 h-4 w-4" />
                向量管理
              </Button>
            </Link>
            <Link to="/skill">
              <Button
                variant={location.pathname === '/skill' ? 'secondary' : 'ghost'}
                className="w-full justify-start"
              >
                <Settings className="mr-2 h-4 w-4" />
                Skill 配置
              </Button>
            </Link>
            <Link to="/debug">
              <Button
                variant={location.pathname === '/debug' ? 'secondary' : 'ghost'}
                className="w-full justify-start"
              >
                <Bug className="mr-2 h-4 w-4" />
                调试面板
              </Button>
            </Link>
            <Link to="/agent-templates">
              <Button
                variant={location.pathname === '/agent-templates' ? 'secondary' : 'ghost'}
                className="w-full justify-start"
              >
                <Brain className="mr-2 h-4 w-4" />
                智能体管理
              </Button>
            </Link>
          </nav>
        </aside>

        <main className="flex-1 ml-64 p-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/knowledge-bases" element={<KnowledgeBases />} />
            <Route path="/documents" element={<Documents />} />
            <Route path="/clean-preview" element={<CleanPreviewPage />} />
            <Route path="/chat" element={<Chat {...chatState} />} />
            <Route path="/memories" element={<MemoryManagement />} />
            <Route path="/excel-documents" element={<ExcelDocuments />} />
            <Route path="/vector" element={<VectorManagement />} />
            <Route path="/skill" element={<SkillConfig />} />
            <Route path="/debug" element={<DebugPanel />} />
            <Route path="/agent-templates" element={<AgentTemplates />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

function Root() {
  return (
    <Router>
      <App />
    </Router>
  );
}

export default Root;
