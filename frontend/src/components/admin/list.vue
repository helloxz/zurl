<template>
    <div class="posts">
        <Notice>
            <ul>
                <li>{{ $t('list.notice1') }}</li>
                <li>{{ $t('list.notice2') }}</li>
                <li>{{ $t('list.notice3') }}</li>
            </ul>
        </Notice>
        <!-- 按钮部分 -->
        <div class="btns">
            <el-button type="primary" @click="addLink">{{ $t('add.link') }}</el-button>
            <!-- <el-button type="danger" @click="confirmCleanData">清空数据</el-button> -->
            <el-button type="danger" @click="delSelectedRows">{{ $t('delete.selected') }}</el-button>

            <div class="search">
                <el-input
                    v-model="search.keyword"
                    style="max-width: 600px"
                    :placeholder="$t('list.search.placeholder')"
                    class="input-with-select"
                    clearable
                    @clear="clearSearch"
                >
                <template #prepend>
                    <el-select v-model="search.filter" :placeholder="$t('list.search.filter.placeholder')" style="width: 120px">
                        <el-option :label="$t('short.url')" value="short_url" />
                        <el-option :label="$t('long.url')" value="long_url" />
                        <el-option :label="$t('list.search.blurry.title')" value="title" />
                    </el-select>
                </template>
                <template #append>
                    <el-button @click="searchKeyword" :icon="Search" />
                </template>
                </el-input>
            </div>
        </div>
        <!-- 按钮部分END -->

        <el-divider />
        <!-- 表格 -->
        <el-table ref="tableRef" :key="tableKey" :data="urlsData" style="width: 100%;margin-top:1em;">
            <!-- <el-table-column fixed prop="id" label="链接ID" width="100">
                <template #default="{row}">
                    <span>{{row.id}}</span>
                </template>
            </el-table-column> -->
            <el-table-column type="selection" width="40" />
            <el-table-column prop="short_url" :label="$t('short.url')" width="100">
                <template #default="{row}">
                    <span :title="$t('click.copy')" @click="copyShortUrl(row.short_url)" class="short-url">
                        <span>{{row.short_url}}</span>
                    </span>
                </template>
            </el-table-column>
            <el-table-column prop="long_url" :label="$t('long.url')"  width="260">
                <template #default="{row}">
                    <div style="white-space: nowrap;overflow: hidden;text-overflow: ellipsis;">
                        <el-link type="info" target="_blank" :href="row.long_url">{{row.long_url}}</el-link>
                    </div>
                </template>
            </el-table-column>

            <el-table-column prop="title" :label="$t('title')"  width="350">
                <template #default="{row}">
                    <span style="white-space: nowrap;overflow: hidden;text-overflow: ellipsis;">{{row.title}}</span>
                </template>
            </el-table-column>

            <!-- 点击次数 -->
            <el-table-column sortable prop="clicks" :label="$t('clicks')"  width="110">
                <template #default="{row}">
                    <span>{{row.clicks}}</span>
                </template>
            </el-table-column>

            <el-table-column sortable prop="updated_at" :label="$t('updated_at')"  width="150">
                <template #default="{row}">
                    <span>{{siteStore.formatDateTime(row.updated_at)}}</span>
                </template>
            </el-table-column>

            <el-table-column sortable prop="expires_at" :label="$t('expires_at')"  width="150">
                <template #default="{row}">
                    <span>{{siteStore.formatDateTime(row.expires_at)}}</span>
                </template>
            </el-table-column>

            <el-table-column prop="is_active" :label="$t('link.enabled')" width="90">
                <template #default="{row}">
                    <el-tag :type="row.is_active === 1 ? 'success' : 'info'">{{ row.is_active === 1 ? $t('link.enabled.yes') : $t('link.enabled.no') }}</el-tag>
                </template>
            </el-table-column>
           
            <el-table-column fixed="right" :label="$t('actions')" min-width="90">
            <template #default="scope">
                <el-button :title="$t('edit')" @click="editLink(scope.row)" size="large" link type="primary" :icon="Edit"></el-button>

                <el-popconfirm @confirm="deletePost(scope)" :title="$t('confirm.delete')" >
                    <template #reference>
                        <el-button :title="$t('delete')" size="large" link type="danger" :icon="Delete" />
                        <!-- <el-button link type="danger" size="small">删除</el-button> -->
                    </template>
                    
                </el-popconfirm>
                
            </template>
            </el-table-column>
        </el-table>
        <!-- 表格END -->

        <!-- 分页 -->
        <div class="page">
            <el-pagination
                :hide-on-single-page="true"
                :page-sizes="[10, 100, 200]"
                v-model:page-size="pageInfo.pageSize"
                @change="getPosts"
                v-model:current-page="pageInfo.currentPage"
                background             
                layout="sizes, prev, pager, next"
                :total="pageInfo.total"
            />
        </div>
        <!-- 分页END -->
    </div>

    <!-- 添加链接对话框 -->
    <el-dialog @close="handleClose" destroy-on-close v-model="addLinkVisible" :title="addLinkTitle" width="400">
        <Add :utype="addLinkType" @finish="handleFinish" :url="linkInfo" />
    </el-dialog>
    <!-- 添加链接对话框END -->
</template>

<script setup>
import {ref,onMounted} from 'vue'
import req, { toForm } from '@/utils/req'
import { useSiteStore } from '@/stores/site';
import { useBaseStore } from '@/stores/base';
import { ElMessage } from 'element-plus';
import Notice from '../notice.vue';
import Add from '@/components/admin/add.vue';
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()
const tableKey = ref(0)
import {
    Delete,
    Edit,
    Search
} from '@element-plus/icons-vue'

const siteStore = useSiteStore()
const baseStore = useBaseStore()

const tableRef = ref(null)

const addLinkVisible = ref(false) // 添加链接对话框是否可见

const urlsData = ref([])

// 搜索字段
const search = ref({
    filter: 'short_url', // 默认查询短链接
    keyword: ''
})

// 复制短链接（支持非根目录部署）
const copyShortUrl = (shortUrl) => {
    const base = (window.__BASE_PATH__ || import.meta.env.VITE_BASE_URL || '').replace(/\/$/, '')
    const url = window.location.protocol + '//' + window.location.host + (base ? base + '/' : '/') + shortUrl
    baseStore.copyText(url)
}

// 弹出框标题
const addLinkTitle = ref(t('add.link'))
const addLinkType = ref("add") // 添加链接类型，默认为添加

// 清空搜索，然后重新获取链接
const clearSearch = ()=>{
    search.value.keyword = ''
    search.value.filter = 'short_url'
    pageInfo.value.currentPage = 1 // 重置当前页为1
    pageInfo.value.pageSize = 10 // 重置每页显示的条数
    getPosts()
}

// 删除选中
const delSelectedRows = ()=>{
    const selectedRows = tableRef.value.getSelectionRows()
    // 如果长度是0
    if( selectedRows.length === 0 ) {
        ElMessage.warning(t('please.select.delete.links'))
        return
    }
    // 筛选出里面的id
    const ids = selectedRows.map(row => row.id)
    let datas = {
        ids: ids
    }
    // 弹出二次确认
    ElMessageBox.confirm(t('delete.confirm.msg'), t('tips'), {
        confirmButtonText: t('confirm'),
        cancelButtonText: t('cancel'),
        type: 'warning'
    }).then(() => {
        req.post("/api/delete/urls", datas)
        .then(res=>{
            if( res.data.code == 200 ) {
                ElMessage.success(t(res.data.msg))
                // 重新获取文章列表
                getPosts()
            }
        })
        .catch(err=>{
            console.log(err)
            ElMessage.error(t("delete.failed"))
        })
    }).catch((err) => {
        // 用户取消
    });
}

// 关闭弹窗
const handleFinish = ()=>{
    addLinkVisible.value = false
    addLinkTitle.value = t('add.link')
    linkInfo.value = {
        long_url: '',
        short_url: '',
        title: '',
        clicks: 0,
        updated_at: '',
        is_active: 1
    }
    getPosts()
}

const handleClose = ()=>{
    addLinkVisible.value = false
    addLinkTitle.value = t('add.link')
    linkInfo.value = {
        long_url: '',
        short_url: '',
        title: '',
        clicks: 0,
        updated_at: '',
        is_active: 1
    }
}

// 单个链接信息
const linkInfo = ref({
    long_url: '',
    short_url: '',
    title: '',
    clicks: 0,
    updated_at: '',
    is_active: 1
})

// 分页信息
const pageInfo = ref({
    total:0,// 总跳数
    pageSize:10,// 每页显示的条数
    currentPage:1,// 当前页
})

// 添加链接
const addLink = ()=>{
    addLinkVisible.value = true
    addLinkTitle.value = t('add.link')
    addLinkType.value = "add"
    linkInfo.value = {
        long_url: '',
        short_url: '',
        title: '',
        clicks: 0,
        updated_at: '',
        is_active: 1
    }
}

// 编辑链接
const editLink = (row)=>{
    console.log(row)
    linkInfo.value = row;
    addLinkVisible.value = true;
    addLinkType.value = "edit"
    addLinkTitle.value = t('edit.link1')
}

// 查询链接
const searchKeyword = ()=>{
    // 如果没有输入内容，则不查询
    if( search.value.keyword.trim() === '' ){
        ElMessage.warning(t("please.enter.query.content"))
        return
    }
    
    let url = "/api/search"
    let params = {
        filter: search.value.filter,
        keyword: search.value.keyword
    }

    req.post(url,params)
    .then(res=>{
        if( res.data.code == 200 ) {
            // 查询成功
            urlsData.value = res.data.data.urls
            pageInfo.value.total = res.data.data.total
            pageInfo.value.currentPage = 1 // 重置当前页为1
            pageInfo.value.pageSize = res.data.data.total
            // 强制刷新表格
            tableKey.value++
        }
        else {
            ElMessage.error(t(res.data.msg))
        }
    })
    .catch(err=>{
        console.log(err)
        ElMessage.error(t("query.failed"))
    })
}

// 删除单篇文章
const deletePost = (index)=>{
    // console.log(index)
    let short_url = index.row.short_url
    let url = "/api/delete/url"
    req.post(url,toForm({short_url:short_url}))
    .then(res=>{
        if(res.data.code == 200){
            ElMessage.success(t(res.data.msg))
            urlsData.value.splice(index.$index, 1)
        }
        else{
            ElMessage.error(t(res.data.msg))
        }
    })
    .catch(err=>{
        console.log(err)
        ElMessage.error(t("delete.failed"))
    })
}

// 编辑单个链接


// 获取文章列表
const getPosts = ()=>{
    // console.log(search.value.keyword);
    // 如果查询关键词不为空，则不要执行后续逻辑
    if( search.value.keyword.trim() !== '' ) {
        // searchKeyword()
        return
    }
    req.get("/api/urls?page="+pageInfo.value.currentPage+"&limit="+pageInfo.value.pageSize)
    .then(res=>{
        if( res.data.code == 200 ) {
            urlsData.value = res.data.data.urls
            pageInfo.value.total = res.data.data.total
            // 强制刷新表格
            tableKey.value++
        }
    })
}


// 清空数据
const confirmCleanData = ()=>{
    ElMessageBox.confirm('此操作将清空所有数据, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
    }).then(() => {
        // 清空数据
        req.post("/api/urls/clear")
        .then(res=>{
            if( res.data.code == 200 ) {
                // 提示成功
                ElMessage.success(t(res.data.msg))
                // 重新获取文章列表
                getPosts()
            }
            else {
                // 提示失败
                ElMessage.error(t(res.data.msg))
            }
        })
    }).catch((err) => {
        // ElMessage.error("操作失败！")
        // 提示取消
        // console.log(err)
    });
}


onMounted(()=>{
    getPosts()
})
</script>

<style scoped>
.short-url{
    cursor: pointer;
}
.search{
    margin-left: 20px;
    display: inline-block;
    width: 400px;
}
.posts{
    width: 100%;
}
.btns{
    margin-top:1em;
}
.dialog-btns{
    display: flex;
    justify-content: center;
    margin-top:1.5em;
}
.post_title{
    /**超出省略号 */
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    width: 350px;
}


.page{
    margin-top:1em;
}
</style>